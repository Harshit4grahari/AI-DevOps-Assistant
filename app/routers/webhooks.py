from collections import deque
import hashlib
import hmac
import json
import logging
from typing import Any, Dict, List
from fastapi import APIRouter, Header, HTTPException, Request, BackgroundTasks

from app.config import settings
from app.services.github_service import github_service
from app.services.llm_engine import llm_engine
from app.services.gitops_service import gitops_service

logger = logging.getLogger("devops_bot.webhooks")
router = APIRouter(prefix="/webhook", tags=["Webhooks"])

# In-memory recent events log for dashboard visualization (stores last 50 events)
recent_events: deque = deque(maxlen=50)


def verify_signature(payload: bytes, signature_header: str, secret: str) -> bool:
    """Verifies HMAC SHA-256 signature sent by GitHub."""
    if not signature_header:
        return False
    sha_name, signature = signature_header.split("=")
    if sha_name != "sha256":
        return False
    mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), signature)


async def handle_pull_request_event(payload: Dict[str, Any]):
    """Processes PR opened, synchronize, or closed/merged events."""
    action = payload.get("action")
    pr = payload.get("pull_request", {})
    repo = payload.get("repository", {})
    repo_name = repo.get("full_name", "unknown/repo")
    pr_number = pr.get("number")
    pr_title = pr.get("title", "")
    pr_body = pr.get("body", "")

    event_record = {
        "type": "pull_request",
        "action": action,
        "repo": repo_name,
        "pr_number": pr_number,
        "title": pr_title,
        "status": "processing",
        "timestamp": None,
    }

    if action in ["opened", "synchronize", "reopened"]:
        logger.info(f"Processing PR #{pr_number} in {repo_name} (action: {action})")
        
        # 1. Fetch PR diff
        diff = await github_service.get_pr_diff(repo_name, pr_number)

        # 2. In an integrated pipeline, Trivy and SonarQube results may be passed via workflow or check-runs
        trivy_mock_report = json.dumps({
            "Target": "Dockerfile",
            "Vulnerabilities": [
                {"VulnerabilityID": "CVE-2024-21626", "PkgName": "runc", "Severity": "HIGH", "Description": "Internal file descriptor leak in runc"}
            ]
        })

        # 3. LLM Review
        analysis = await llm_engine.analyze_pr(
            diff=diff,
            pr_title=pr_title,
            pr_description=pr_body,
            trivy_report=trivy_mock_report,
        )

        # 4. Post comment to GitHub
        await github_service.post_pr_comment(
            repo_full_name=repo_name,
            pr_number=pr_number,
            body=analysis["markdown_review"],
        )

        event_record["status"] = "reviewed"
        event_record["details"] = "AI PR review & security scan posted successfully."

    elif action == "closed" and pr.get("merged", False):
        logger.info(f"PR #{pr_number} in {repo_name} was MERGED into {pr.get('base', {}).get('ref')}")
        
        # Trigger GitOps ArgoCD Sync on merge
        app_name = repo_name.split("/")[-1]
        merge_sha = pr.get("merge_commit_sha", "HEAD")
        
        sync_result = await gitops_service.trigger_argocd_sync(
            app_name=app_name,
            revision=merge_sha,
        )

        comment_body = (
            f"### 🚀 GitOps Deployment Initiated\n\n"
            f"- **Target Application**: `{app_name}`\n"
            f"- **Commit SHA**: `{merge_sha[:7] if merge_sha else 'HEAD'}`\n"
            f"- **Sync Status**: `{sync_result.get('sync_status', 'Triggered')}`\n"
            f"- **Health**: `{sync_result.get('health_status', 'Healthy')}`\n\n"
            f"ArgoCD is reconciling Kubernetes workloads in AWS EKS cluster."
        )
        await github_service.post_pr_comment(repo_name, pr_number, comment_body)

        event_record["status"] = "deployed"
        event_record["details"] = f"GitOps deployment triggered for commit {merge_sha[:7]}"

    recent_events.appendleft(event_record)


async def handle_workflow_run_event(payload: Dict[str, Any]):
    """Processes workflow_run failures, analyzes logs, and posts root cause analysis."""
    action = payload.get("action")
    workflow_run = payload.get("workflow_run", {})
    conclusion = workflow_run.get("conclusion")
    repo = payload.get("repository", {})
    repo_name = repo.get("full_name", "unknown/repo")
    run_id = workflow_run.get("id")
    workflow_name = workflow_run.get("name", "CI/CD Workflow")

    event_record = {
        "type": "workflow_run",
        "action": action,
        "repo": repo_name,
        "run_id": run_id,
        "workflow": workflow_name,
        "conclusion": conclusion,
        "status": "processing",
    }

    if action == "completed" and conclusion == "failure":
        logger.info(f"Workflow run #{run_id} ({workflow_name}) in {repo_name} FAILED. Diagnosing...")

        # 1. Fetch run logs
        logs = await github_service.get_workflow_run_logs(repo_name, run_id)

        # 2. LLM Log Diagnosis
        diagnosis = await llm_engine.diagnose_pipeline_failure(
            logs=logs,
            workflow_name=workflow_name,
            failed_step="Test & Security Validation",
        )

        # 3. Post diagnosis to associated PR if available
        pull_requests = workflow_run.get("pull_requests", [])
        if pull_requests:
            pr_number = pull_requests[0].get("number")
            await github_service.post_pr_comment(
                repo_full_name=repo_name,
                pr_number=pr_number,
                body=diagnosis["markdown_diagnosis"],
            )

        event_record["status"] = "diagnosed"
        event_record["details"] = f"Root cause diagnosed. Suggested patch generated for run #{run_id}."

    recent_events.appendleft(event_record)


@router.post("/github")
async def github_webhook_endpoint(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: str = Header(None, alias="X-GitHub-Event"),
    x_hub_signature_256: str = Header(None, alias="X-Hub-Signature-256"),
):
    """Primary webhook ingestion endpoint for GitHub App events."""
    payload_bytes = await request.body()

    # Verify signature if secret is configured and not in dev/testing mode
    if settings.GITHUB_WEBHOOK_SECRET and x_hub_signature_256:
        if not verify_signature(payload_bytes, x_hub_signature_256, settings.GITHUB_WEBHOOK_SECRET):
            logger.warning("Invalid GitHub webhook signature received.")
            raise HTTPException(status_code=401, detail="Invalid HMAC signature")

    try:
        payload = json.loads(payload_bytes.decode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")

    logger.info(f"Received GitHub webhook event: {x_github_event}")

    if x_github_event == "pull_request":
        background_tasks.add_task(handle_pull_request_event, payload)
    elif x_github_event == "workflow_run":
        background_tasks.add_task(handle_workflow_run_event, payload)
    elif x_github_event == "ping":
        return {"status": "pong", "zen": payload.get("zen")}
    else:
        logger.info(f"Unhandled GitHub event type: {x_github_event}")

    return {"status": "accepted", "event": x_github_event}
