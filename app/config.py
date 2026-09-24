from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "AI DevOps Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # GitHub App & OAuth Credentials
    GITHUB_APP_ID: Optional[str] = None
    GITHUB_APP_PRIVATE_KEY: Optional[str] = None  # PEM string or path to .pem
    GITHUB_WEBHOOK_SECRET: Optional[str] = "devops-assistant-webhook-secret"
    GITHUB_API_URL: str = "https://api.github.com"
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    GITHUB_REDIRECT_URI: Optional[str] = None
    JWT_SECRET_KEY: str = "devops-assistant-jwt-secret-key-2026"

    # LLM Settings
    LLM_PROVIDER: str = "gemini"  # "gemini" or "openai" or "mock"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-pro"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    LLM_TEMPERATURE: float = 0.2

    # GitOps & ArgoCD Settings
    ARGOCD_SERVER_URL: Optional[str] = "https://argocd.internal.infra"
    ARGOCD_AUTH_TOKEN: Optional[str] = None
    GITOPS_REPO_URL: Optional[str] = "https://github.com/org/gitops-manifests"
    GITOPS_TARGET_BRANCH: str = "main"

    # Security Scanners Config
    ENABLE_AUTO_FIX_SUGGESTIONS: bool = True
    MAX_DIFF_LINES_TO_ANALYZE: int = 1500
    MAX_LOG_LINES_TO_ANALYZE: int = 2000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
