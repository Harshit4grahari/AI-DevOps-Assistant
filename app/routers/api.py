from typing import Any, Dict, Optional
from fastapi import APIRouter, Body
from pydantic import BaseModel

from app.config import settings
from app.services.llm_engine import llm_engine
from app.services.gitops_service import gitops_service
from app.routers.webhooks import recent_events

router = APIRouter(prefix="/api", tags=["Assistant API"])


class PRAnalysisRequest(BaseModel):
    diff: str
    title: str = "Feature: Add Authentication Service"
    description: str = "Implements user auth endpoints and database access"
    trivy_report: Optional[str] = None
    sonarqube_report: Optional[str] = None


class FetchPRRequest(BaseModel):
    pr_url: str
    token: Optional[str] = None


class LogDiagnosisRequest(BaseModel):
    logs: str
    workflow_name: str = "Test & Security Pipeline"
    failed_step: Optional[str] = "Run pytest"


class WebhookSimulationRequest(BaseModel):
    event_type: str  # "pull_request" or "workflow_run"
    action: str = "opened"
    repo_name: str = "octocat/hello-world"
    pr_number: int = 42


@router.post("/fetch-pr")
async def fetch_pr_endpoint(request: FetchPRRequest) -> Dict[str, Any]:
    """Fetches PR metadata and unified diff directly from a GitHub PR URL."""
    import re
    # Match https://github.com/owner/repo/pull/123 or owner/repo#123
    pattern = r"(?:https?://github\.com/)?([^/]+/[^/]+)(?:/pull/|#)(\d+)"
    match = re.search(pattern, request.pr_url.strip())
    
    if not match:
        return {
            "status": "error",
            "message": "Invalid PR URL format. Expected: https://github.com/owner/repo/pull/123 or owner/repo#123"
        }

    repo_full_name = match.group(1)
    pr_number = int(match.group(2))

    diff = await github_service.get_pr_diff(repo_full_name, pr_number, request.token)
    
    # Try fetching PR title from GitHub API if token or public
    title = f"PR #{pr_number} in {repo_full_name}"
    description = ""
    try:
        import httpx
        url = f"{settings.GITHUB_API_URL}/repos/{repo_full_name}/pulls/{pr_number}"
        headers = {"Accept": "application/vnd.github.v3+json"}
        if request.token:
            headers["Authorization"] = f"token {request.token}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, headers=headers)
            if res.status_code == 200:
                data = res.json()
                title = data.get("title", title)
                description = data.get("body", "")
    except Exception:
        pass

    return {
        "status": "success",
        "repo": repo_full_name,
        "pr_number": pr_number,
        "title": title,
        "description": description,
        "diff": diff
    }


@router.get("/status")
async def get_system_status() -> Dict[str, Any]:
    """Returns runtime health and configuration status of the DevOps assistant."""
    argo_status = await gitops_service.get_application_health("sample-microservice")
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_configured": bool(settings.GEMINI_API_KEY or settings.OPENAI_API_KEY),
        "github_app_configured": bool(settings.GITHUB_APP_ID and settings.GITHUB_APP_PRIVATE_KEY),
        "argocd_configured": bool(settings.ARGOCD_AUTH_TOKEN),
        "argocd_health": argo_status.get("health", {}).get("status", "Healthy (Simulated)"),
    }


@router.get("/events")
async def get_recent_events() -> list:
    """Returns the buffer of recent webhook and pipeline actions for the dashboard feed."""
    return list(recent_events)


@router.post("/analyze/diff")
async def analyze_diff_endpoint(request: PRAnalysisRequest) -> Dict[str, Any]:
    """Direct API endpoint to review a diff with Trivy/SonarQube context."""
    return await llm_engine.analyze_pr(
        diff=request.diff,
        pr_title=request.title,
        pr_description=request.description,
        trivy_report=request.trivy_report,
        sonarqube_report=request.sonarqube_report,
    )


@router.post("/analyze/logs")
async def analyze_logs_endpoint(request: LogDiagnosisRequest) -> Dict[str, Any]:
    """Direct API endpoint to diagnose CI/CD build failure logs."""
    return await llm_engine.diagnose_pipeline_failure(
        logs=request.logs,
        workflow_name=request.workflow_name,
        failed_step=request.failed_step,
    )


@router.post("/simulate-webhook")
async def simulate_webhook_event(sim: WebhookSimulationRequest) -> Dict[str, Any]:
    """Simulates a webhook trigger for testing the dashboard and assistant logic."""
    if sim.event_type == "pull_request":
        record = {
            "type": "pull_request",
            "action": sim.action,
            "repo": sim.repo_name,
            "pr_number": sim.pr_number,
            "title": "PR #42: Modernize authentication architecture",
            "status": "reviewed" if sim.action != "closed" else "deployed",
            "details": "AI PR review generated with 2 security findings & suggested patches." if sim.action != "closed" else "GitOps ArgoCD sync dispatched to AWS EKS.",
        }
    else:
        record = {
            "type": "workflow_run",
            "action": "completed",
            "repo": sim.repo_name,
            "run_id": 98765432,
            "workflow": "CI / Automated Tests & Scans",
            "conclusion": "failure",
            "status": "diagnosed",
            "details": "Root cause: AssertionError in test_auth.py:42. Patch generated.",
        }
    
    recent_events.appendleft(record)
    return {"status": "simulated", "event": record}
