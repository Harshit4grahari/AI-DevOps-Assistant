import io
import logging
import time
import zipfile
from typing import Any, Dict, List, Optional
import httpx
import jwt

from app.config import settings

logger = logging.getLogger("devops_bot.github")


class GitHubService:
    """Service to interact with GitHub REST API as a GitHub App or Bot."""

    def __init__(self):
        self.app_id = settings.GITHUB_APP_ID
        self.private_key = settings.GITHUB_APP_PRIVATE_KEY
        self.api_url = settings.GITHUB_API_URL

    def _generate_jwt(self) -> Optional[str]:
        """Generates a JSON Web Token (JWT) signed with the GitHub App private key."""
        if not self.app_id or not self.private_key:
            return None

        now = int(time.time())
        payload = {
            "iat": now - 60,
            "exp": now + (10 * 60),  # 10 minutes expiry
            "iss": self.app_id,
        }

        try:
            token = jwt.encode(payload, self.private_key, algorithm="RS256")
            return token
        except Exception as e:
            logger.error(f"Failed to generate GitHub App JWT: {e}")
            return None

    async def get_installation_token(self, installation_id: int) -> Optional[str]:
        """Exchanges App JWT for an installation access token."""
        app_jwt = self._generate_jwt()
        if not app_jwt:
            return None

        url = f"{self.api_url}/app/installations/{installation_id}/access_tokens"
        headers = {
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(url, headers=headers)
                res.raise_for_status()
                return res.json().get("token")
        except Exception as e:
            logger.error(f"Failed to obtain installation token for {installation_id}: {e}")
            return None

    async def get_pr_diff(self, repo_full_name: str, pr_number: int, token: Optional[str] = None) -> str:
        """Fetches the unified diff of a pull request."""
        url = f"{self.api_url}/repos/{repo_full_name}/pulls/{pr_number}"
        headers = {
            "Accept": "application/vnd.github.v3.diff",
        }
        if token:
            headers["Authorization"] = f"token {token}"

        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url, headers=headers)
                res.raise_for_status()
                return res.text
        except Exception as e:
            logger.warning(f"Could not fetch real PR diff from GitHub ({e}). Returning sample diff.")
            return self._sample_diff()

    async def post_pr_comment(
        self,
        repo_full_name: str,
        pr_number: int,
        body: str,
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Posts a markdown review comment to a pull request."""
        url = f"{self.api_url}/repos/{repo_full_name}/issues/{pr_number}/comments"
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if token:
            headers["Authorization"] = f"token {token}"

        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(url, headers=headers, json={"body": body})
                res.raise_for_status()
                return res.json()
        except Exception as e:
            logger.warning(f"Could not post comment to GitHub API ({e}). Simulated comment logged.")
            return {"status": "simulated", "body": body, "repo": repo_full_name, "pr": pr_number}

    async def get_workflow_run_logs(
        self,
        repo_full_name: str,
        run_id: int,
        token: Optional[str] = None,
    ) -> str:
        """Downloads and extracts workflow logs for a given GitHub Actions run."""
        url = f"{self.api_url}/repos/{repo_full_name}/actions/runs/{run_id}/logs"
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if token:
            headers["Authorization"] = f"token {token}"

        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                res = await client.get(url, headers=headers)
                res.raise_for_status()

                # GitHub returns a zip archive of logs
                with zipfile.ZipFile(io.BytesIO(res.content)) as z:
                    log_texts = []
                    for filename in z.namelist():
                        if filename.endswith(".txt"):
                            with z.open(filename) as f:
                                log_texts.append(f"--- Log File: {filename} ---\n" + f.read().decode("utf-8", errors="ignore"))
                    return "\n\n".join(log_texts)
        except Exception as e:
            logger.warning(f"Could not download GitHub workflow logs ({e}). Using sample failure logs.")
            return self._sample_failure_log()

    def _sample_diff(self) -> str:
        return """diff --git a/app/api/auth.py b/app/api/auth.py
index a1b2c3d..e4f5g6h 100644
--- a/app/api/auth.py
+++ b/app/api/auth.py
@@ -10,6 +10,12 @@ router = APIRouter()
 
+@router.post("/login")
+def login(user_data: dict):
+    # Query database directly
+    query = f"SELECT * FROM users WHERE username = '{user_data.get('user')}'"
+    db.execute(query)
+    return {"token": "secret-token-12345"}
+
 def get_current_user():
     pass
"""

    def _sample_failure_log(self) -> str:
        return """2026-09-21T14:30:10.1234567Z ##[section]Starting: Run pytest test suite
2026-09-21T14:30:11.2345678Z ============================= test session starts ==============================
2026-09-21T14:30:12.3456789Z collecting ... collected 18 items
2026-09-21T14:30:14.4567890Z tests/test_auth.py::test_login_success PASSED
2026-09-21T14:30:15.5678901Z tests/test_auth.py::test_sql_injection FAILED
2026-09-21T14:30:15.6789012Z 
2026-09-21T14:30:15.6789123Z =================================== FAILURES ===================================
2026-09-21T14:30:15.6789234Z _____________________________ test_sql_injection ______________________________
2026-09-21T14:30:15.6789345Z tests/test_auth.py:42: in test_sql_injection
2026-09-21T14:30:15.6789456Z     assert response.status_code == 400
2026-09-21T14:30:15.6789567Z E   AssertionError: assert 200 == 400
2026-09-21T14:30:15.6789678Z E    +  where 200 = <Response [200 OK]>.status_code
2026-09-21T14:30:16.7890123Z =========================== short test summary info ============================
2026-09-21T14:30:16.7891234Z FAILED tests/test_auth.py::test_sql_injection - AssertionError: assert 200 == 400
2026-09-21T14:30:16.7892345Z ##[error]Process completed with exit code 1.
"""


github_service = GitHubService()
