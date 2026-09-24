import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from app.config import settings
from app.routers import webhooks, api

# Prometheus Metrics Definitions
REQUEST_COUNT = Counter("devops_bot_http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("devops_bot_http_latency_seconds", "HTTP request latency in seconds", ["endpoint"])
PR_REVIEWS_TOTAL = Counter("devops_bot_pr_reviews_total", "Total Pull Requests reviewed by AI DevOps Assistant", ["status"])
FAILURE_DIAGNOSES_TOTAL = Counter("devops_bot_failure_diagnoses_total", "Total CI/CD pipeline failures diagnosed", ["workflow"])
GITOPS_SYNCS_TOTAL = Counter("devops_bot_gitops_syncs_total", "Total GitOps deployments triggered on merge", ["app_name"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    print(f"[{settings.APP_NAME}] Starting up on {settings.HOST}:{settings.PORT}")
    print(f"[{settings.APP_NAME}] LLM Provider configured: {settings.LLM_PROVIDER}")
    yield
    # Teardown actions
    print(f"[{settings.APP_NAME}] Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise AI-Powered DevOps Assistant for GitHub Actions, ArgoCD GitOps, and Kubernetes.",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def prometheus_metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    endpoint = request.url.path
    # Group static or health paths to avoid metric explosion
    if endpoint.startswith("/static"):
        endpoint = "/static/*"

    REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, status=response.status_code).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
    return response


# Include Routers
from app.routers import webhooks, api, auth

app.include_router(webhooks.router)
app.include_router(api.router)
app.include_router(auth.router)


@app.get("/healthz", tags=["Observability"])
async def health_check():
    """Kubernetes liveness and readiness probe endpoint."""
    return {"status": "healthy", "service": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/metrics", tags=["Observability"])
async def metrics_endpoint():
    """Prometheus metrics scrape endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Mount Static Files & Dashboard
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", tags=["Dashboard"])
async def serve_dashboard():
    """Serves the modern operations dashboard."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AI DevOps Assistant is operational. UI assets are initializing."}
