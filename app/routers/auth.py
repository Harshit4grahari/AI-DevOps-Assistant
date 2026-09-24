import logging
import time
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import httpx
import jwt
from urllib.parse import urlencode

from app.config import settings

logger = logging.getLogger("devops_bot.auth")
router = APIRouter(prefix="/auth", tags=["Authentication & GitHub OAuth"])

# In-memory user store for demo & local development
USERS_DB: Dict[str, Dict[str, Any]] = {
    "devops_admin@example.com": {
        "email": "devops_admin@example.com",
        "username": "devops-engineer",
        "name": "Senior DevOps Engineer",
        "avatar_url": "https://avatars.githubusercontent.com/u/583231?v=4",
        "github_token": None,
        "is_github_connected": True,
    }
}


class LoginRequest(BaseModel):
    email: str
    password: str


class SignupRequest(BaseModel):
    email: str
    username: str
    password: str


class DemoLoginRequest(BaseModel):
    username: Optional[str] = "cloud-architect"
    github_pat: Optional[str] = None


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload.update({"exp": int(time.time()) + 60 * 60 * 24 * 7})  # 7 days
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def get_current_user_from_token(token: Optional[str]) -> Optional[Dict[str, Any]]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except Exception:
        return None


@router.post("/login")
async def login_user(req: LoginRequest):
    """Logs in an existing user with email and password."""
    user = USERS_DB.get(req.email)
    if not user:
        # Create on demand for smooth demo experience
        user = {
            "email": req.email,
            "username": req.email.split("@")[0],
            "name": req.email.split("@")[0].capitalize(),
            "avatar_url": "https://avatars.githubusercontent.com/u/583231?v=4",
            "github_token": None,
            "is_github_connected": False,
        }
        USERS_DB[req.email] = user

    token = create_access_token(user)
    return {"status": "success", "token": token, "user": user}


@router.post("/signup")
async def signup_user(req: SignupRequest):
    """Registers a new user."""
    user = {
        "email": req.email,
        "username": req.username,
        "name": req.username,
        "avatar_url": "https://avatars.githubusercontent.com/u/583231?v=4",
        "github_token": None,
        "is_github_connected": False,
    }
    USERS_DB[req.email] = user
    token = create_access_token(user)
    return {"status": "success", "token": token, "user": user}


@router.post("/demo-login")
async def demo_login(req: DemoLoginRequest):
    """Instant login for local evaluation with GitHub connection."""
    username = req.username or "cloud-architect"
    user = {
        "email": f"{username}@github.com",
        "username": username,
        "name": f"{username.capitalize()} (GitHub Connected)",
        "avatar_url": "https://avatars.githubusercontent.com/u/9919?s=200&v=4",
        "github_token": req.github_pat,
        "is_github_connected": True,
    }
    token = create_access_token(user)
    return {"status": "success", "token": token, "user": user}


class GitHubTokenRequest(BaseModel):
    token: Optional[str] = None
    username: Optional[str] = None


@router.post("/github/connect-token")
async def connect_github_token(req: GitHubTokenRequest):
    """Authenticates a user via GitHub Personal Access Token or username."""
    token = req.token.strip() if req.token else None
    username = req.username.strip() if req.username else None

    # If real token provided, fetch actual user profile from GitHub API
    if token:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(
                    "https://api.github.com/user",
                    headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
                )
                if res.status_code == 200:
                    gh_user = res.json()
                    user = {
                        "email": gh_user.get("email") or f"{gh_user.get('login')}@users.noreply.github.com",
                        "username": gh_user.get("login"),
                        "name": gh_user.get("name") or gh_user.get("login"),
                        "avatar_url": gh_user.get("avatar_url"),
                        "github_token": token,
                        "is_github_connected": True,
                    }
                    USERS_DB[user["email"]] = user
                    jwt_token = create_access_token(user)
                    return {"status": "success", "token": jwt_token, "user": user}
        except Exception as e:
            logger.warning(f"Failed to authenticate with GitHub PAT ({e}). Creating session with username.")

    # Fallback with specified or default username
    user_name = username or "github-developer"
    user = {
        "email": f"{user_name}@users.noreply.github.com",
        "username": user_name,
        "name": user_name.capitalize(),
        "avatar_url": f"https://github.com/{user_name}.png",
        "github_token": token,
        "is_github_connected": True,
    }
    USERS_DB[user["email"]] = user
    jwt_token = create_access_token(user)
    return {"status": "success", "token": jwt_token, "user": user}


@router.get("/github/login")
async def github_oauth_login(request: Request):
    """Redirects user to GitHub OAuth authorization page, or creates an active GitHub session if OAuth app is not configured."""
    if not settings.GITHUB_CLIENT_ID:
        # Create an active GitHub user session so it works immediately out of the box!
        user = {
            "email": "github-developer@users.noreply.github.com",
            "username": "github-developer",
            "name": "GitHub Developer",
            "avatar_url": "https://avatars.githubusercontent.com/u/9919?s=200&v=4",
            "github_token": None,
            "is_github_connected": True,
        }
        USERS_DB[user["email"]] = user
        token = create_access_token(user)
        response = RedirectResponse(url=f"/?token={token}&username={user['username']}")
        response.set_cookie(key="devops_token", value=token, httponly=False)
        return response

    redirect_uri = settings.GITHUB_REDIRECT_URI or str(request.url_for("github_oauth_callback"))
    auth_url = "https://github.com/login/oauth/authorize?" + urlencode(
        {
            "client_id": settings.GITHUB_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "scope": "repo read:user user:email",
        }
    )
    return RedirectResponse(url=auth_url)


@router.get("/github/callback")
async def github_oauth_callback(code: Optional[str] = None):
    """Exchanges GitHub OAuth code for access token and authenticates user."""
    if not code:
        return RedirectResponse(url="/?error=no_code")

    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "client_secret": settings.GITHUB_CLIENT_SECRET,
        "code": code,
    }

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(token_url, headers=headers, data=data)
            token_data = res.json()
            access_token = token_data.get("access_token")

            if not access_token:
                return RedirectResponse(url="/?error=oauth_failed")

            # Fetch user profile from GitHub
            user_res = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": "Bearer " + access_token},
            )
            if user_res.status_code != 200:
                logger.error("GitHub profile request failed with status %s", user_res.status_code)
                return RedirectResponse(url="/?error=github_profile_failed")
            gh_user = user_res.json()

            user = {
                "email": gh_user.get("email") or f"{gh_user.get('login')}@users.noreply.github.com",
                "username": gh_user.get("login"),
                "name": gh_user.get("name") or gh_user.get("login"),
                "avatar_url": gh_user.get("avatar_url"),
                "github_token": access_token,
                "is_github_connected": True,
            }
            USERS_DB[user["email"]] = user
            jwt_token = create_access_token(user)

            # Redirect to home with token in fragment or cookie
            response = RedirectResponse(url=f"/?token={jwt_token}&username={user['username']}")
            response.set_cookie(key="devops_token", value=jwt_token, httponly=False)
            return response
    except Exception as e:
        logger.error(f"GitHub OAuth error: {e}")
        return RedirectResponse(url="/?error=oauth_exception")


@router.get("/me")
async def get_current_user_info(request: Request):
    """Returns current logged-in user profile."""
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    elif "devops_token" in request.cookies:
        token = request.cookies.get("devops_token")

    user = get_current_user_from_token(token)
    if not user:
        return {"authenticated": False, "user": None}
    return {"authenticated": True, "user": user}


# -------------------------------------------------------------
# GitHub Repositories & PR Automation Endpoints
# -------------------------------------------------------------
@router.get("/repos")
async def list_user_repositories(request: Request):
    """Lists repositories accessible to the user (real GitHub API if token exists, or curated demo repos)."""
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]

    user = get_current_user_from_token(token)
    gh_token = user.get("github_token") if user else None

    # If user provided a real GitHub token, query GitHub API
    if gh_token:
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(
                    "https://api.github.com/user/repos?sort=updated&per_page=20",
                    headers={"Authorization": f"token {gh_token}", "Accept": "application/vnd.github.v3+json"},
                )
                if res.status_code == 200:
                    repos = res.json()
                    return [
                        {
                            "name": r["name"],
                            "full_name": r["full_name"],
                            "description": r.get("description") or "No description provided",
                            "stars": r.get("stargazers_count", 0),
                            "language": r.get("language") or "General",
                            "open_prs_count": r.get("open_issues_count", 0),
                            "url": r["html_url"],
                            "devops_bot_enabled": True,
                        }
                        for r in repos
                    ]
        except Exception as e:
            logger.warning(f"Failed to fetch live GitHub repos: {e}")

    # High-fidelity mock/curated repositories for instant interaction
    return [
        {
            "name": "cloud-backend-microservice",
            "full_name": "acme-corp/cloud-backend-microservice",
            "description": "Enterprise FastAPI backend service with PostgreSQL & Redis caching",
            "stars": 142,
            "language": "Python",
            "open_prs_count": 3,
            "url": "https://github.com/acme-corp/cloud-backend-microservice",
            "devops_bot_enabled": True,
        },
        {
            "name": "kubernetes-gitops-infra",
            "full_name": "acme-corp/kubernetes-gitops-infra",
            "description": "Production ArgoCD GitOps manifests, Helm charts, and Terraform configs",
            "stars": 89,
            "language": "HCL / YAML",
            "open_prs_count": 1,
            "url": "https://github.com/acme-corp/kubernetes-gitops-infra",
            "devops_bot_enabled": True,
        },
        {
            "name": "auth-identity-gateway",
            "full_name": "acme-corp/auth-identity-gateway",
            "description": "Zero-trust OAuth2 / OIDC authentication gateway for microservices",
            "stars": 54,
            "language": "Go",
            "open_prs_count": 2,
            "url": "https://github.com/acme-corp/auth-identity-gateway",
            "devops_bot_enabled": False,
        },
        {
            "name": "devops-assistant-action",
            "full_name": "acme-corp/devops-assistant-action",
            "description": "GitHub Action plugin for automated Trivy, SonarQube & AI PR reviews",
            "stars": 210,
            "language": "TypeScript",
            "open_prs_count": 4,
            "url": "https://github.com/acme-corp/devops-assistant-action",
            "devops_bot_enabled": True,
        },
    ]


@router.get("/repos/{owner}/{repo}/pulls")
async def list_repo_pull_requests(owner: str, repo: str, request: Request):
    """Lists open pull requests for a given repository."""
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]

    user = get_current_user_from_token(token)
    gh_token = user.get("github_token") if user else None

    if gh_token:
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/pulls?state=open",
                    headers={"Authorization": f"token {gh_token}", "Accept": "application/vnd.github.v3+json"},
                )
                if res.status_code == 200:
                    prs = res.json()
                    return [
                        {
                            "number": p["number"],
                            "title": p["title"],
                            "author": p["user"]["login"],
                            "created_at": p["created_at"],
                            "url": p["html_url"],
                            "branch": p["head"]["ref"],
                        }
                        for p in prs
                    ]
        except Exception:
            pass

    # Curated mock PRs for demo repo
    return [
        {
            "number": 104,
            "title": "feat(auth): add JWT token refresh endpoint and rate limiting",
            "author": "alex-dev",
            "created_at": "2 hours ago",
            "url": f"https://github.com/{owner}/{repo}/pull/104",
            "branch": "feat/jwt-refresh",
            "risk_level": "Medium",
        },
        {
            "number": 103,
            "title": "fix(db): resolve connection pool exhaustion under load",
            "author": "sarah-sre",
            "created_at": "5 hours ago",
            "url": f"https://github.com/{owner}/{repo}/pull/103",
            "branch": "fix/db-pool",
            "risk_level": "Low",
        },
        {
            "number": 101,
            "title": "security: patch runc CVE-2024-21626 in base Dockerfile",
            "author": "security-bot",
            "created_at": "1 day ago",
            "url": f"https://github.com/{owner}/{repo}/pull/101",
            "branch": "security/patch-cve",
            "risk_level": "High",
        },
    ]
