import hashlib
import hmac
import json
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.routers.webhooks import verify_signature

client = TestClient(app)


def test_verify_signature():
    secret = "test-secret-key"
    payload = b'{"action": "opened"}'
    valid_sig = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    invalid_sig = "sha256=badbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbad"

    assert verify_signature(payload, valid_sig, secret) is True
    assert verify_signature(payload, invalid_sig, secret) is False
    assert verify_signature(payload, "", secret) is False


def test_github_webhook_ping():
    payload = {"zen": "Keep it logically awesome."}
    payload_bytes = json.dumps(payload).encode()
    secret = settings.GITHUB_WEBHOOK_SECRET
    sig = "sha256=" + hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()

    response = client.post(
        "/webhook/github",
        content=payload_bytes,
        headers={
            "X-GitHub-Event": "ping",
            "X-Hub-Signature-256": sig,
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "pong"
    assert response.json()["zen"] == "Keep it logically awesome."


def test_github_webhook_pull_request():
    payload = {
        "action": "opened",
        "pull_request": {
            "number": 101,
            "title": "Fix memory leak in buffer",
            "body": "Replaced unbounded list with deque",
        },
        "repository": {
            "full_name": "acme/web-service",
        },
    }
    payload_bytes = json.dumps(payload).encode()
    secret = settings.GITHUB_WEBHOOK_SECRET
    sig = "sha256=" + hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()

    response = client.post(
        "/webhook/github",
        content=payload_bytes,
        headers={
            "X-GitHub-Event": "pull_request",
            "X-Hub-Signature-256": sig,
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
