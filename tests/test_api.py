import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "AI DevOps Assistant" in data["service"]


def test_prometheus_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "devops_bot_http_requests_total" in response.text


def test_system_status():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "llm_provider" in data
    assert "argocd_health" in data


def test_analyze_diff_api():
    payload = {
        "title": "feat: add user query",
        "description": "testing diff analysis",
        "diff": """diff --git a/app.py b/app.py
+query = f"SELECT * FROM users WHERE id = '{user_id}'"
""",
        "trivy_report": '{"Vulnerabilities": [{"VulnerabilityID": "CVE-2024-0001", "Severity": "HIGH"}]}'
    }
    response = client.post("/api/analyze/diff", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "markdown_review" in data
    assert "Security" in data["markdown_review"] or "AI DevOps Assistant" in data["markdown_review"]


def test_analyze_logs_api():
    payload = {
        "workflow_name": "CI Tests",
        "failed_step": "Run Pytest",
        "logs": """FAILURES: test_auth.py:42
AssertionError: assert 200 == 400
Process completed with exit code 1."""
    }
    response = client.post("/api/analyze/logs", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "markdown_diagnosis" in data


def test_webhook_simulation():
    payload = {
        "event_type": "pull_request",
        "action": "opened",
        "repo_name": "test/repo",
        "pr_number": 99
    }
    response = client.post("/api/simulate-webhook", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "simulated"
    assert data["event"]["pr_number"] == 99
