# ⚡ AI-Powered DevOps Assistant

> An AI-powered GitHub App, CI/CD Guardian, and GitOps Automation Engine that reviews Pull Requests, analyzes CI/CD failures, automates Kubernetes deployments, and provides real-time DevOps observability.

![AI DevOps Assistant](https://img.shields.io/badge/AI-DevOps%20Assistant-blueviolet)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Production-green)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![Kubernetes](https://img.shields.io/badge/Kubernetes-EKS-326CE5)
![Terraform](https://img.shields.io/badge/Terraform-Infrastructure-7B42BC)
![ArgoCD](https://img.shields.io/badge/ArgoCD-GitOps-orange)
![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C)

---

## 🌐 Live Demo

🚀 **Try the AI-Powered DevOps Assistant live:**

👉 [**Launch AI DevOps Assistant**](https://ai-devops-assistant-murex.vercel.app/)

> Explore the dashboard, test AI-powered PR review, CI/CD failure diagnosis, and the DevOps simulation features directly in your browser.

---

## 🚀 Overview

The **AI-Powered DevOps Assistant** integrates directly into a GitHub repository's development and deployment pipeline.

It combines:

* 🤖 AI-powered Pull Request reviews
* 🔐 Automated security analysis
* 🚨 CI/CD failure diagnosis
* 🐳 Docker image automation
* ☁️ AWS EKS deployment
* 🔄 GitOps with ArgoCD
* 🏗️ Infrastructure as Code with Terraform
* 📊 Prometheus + Grafana monitoring
* 🖥️ Real-time DevOps operations dashboard
* 🔗 GitHub webhook automation

The system is designed to automate repetitive DevOps tasks while giving developers actionable explanations and suggested fixes.

---

# 🏗️ System Architecture

```mermaid
flowchart TD

    subgraph GitHub["GitHub Ecosystem"]
        PR[Pull Request Opened / Synchronized]
        GHA[GitHub Actions: Lint, Test, Trivy, SonarQube]
        Merge[PR Merged into main]
        Fail[Workflow Run Failure]
    end

    subgraph DevOpsBot["AI DevOps Assistant Service"]
        WH[Webhook & Event Gateway]
        LLM[LLM Engine: Gemini / OpenAI]
        PRReviewer[PR Diff & Security Scan Analyzer]
        LogAnalyzer[CI/CD Failure Diagnostic Engine]
        GitOpsSync[GitOps & ArgoCD Orchestrator]
        Dashboard[Operations Dashboard & Simulator]
    end

    subgraph GitOpsK8s["GitOps & Kubernetes"]
        ECR[Amazon ECR]
        ArgoCD[ArgoCD GitOps Controller]
        K8sCluster[AWS EKS Workloads]
    end

    subgraph MonitoringInfra["AWS Infrastructure & Observability"]
        TF[Terraform]
        Prom[Prometheus]
        Graf[Grafana]
    end

    PR -->|Webhook / Action| WH
    GHA -->|SARIF / JSON + Diffs| PRReviewer
    PRReviewer --> LLM
    LLM -->|PR Review + Suggestions| PR

    Fail -->|Workflow Failure + Logs| LogAnalyzer
    LogAnalyzer --> LLM
    LLM -->|Root Cause + Fix Patch| PR

    Merge -->|CI/CD on Merge| ECR
    ECR --> GitOpsSync
    GitOpsSync -->|Image Tag Promotion| ArgoCD
    ArgoCD -->|Sync & Deploy| K8sCluster

    TF --> K8sCluster
    K8sCluster --> Prom
    Prom --> Graf

    WH --> Dashboard
```

The architecture connects GitHub events, the FastAPI AI service, LLM analysis, GitHub Actions, AWS infrastructure, Kubernetes, ArgoCD, and monitoring into one DevOps workflow.

---

# 🌟 Key Features

## 1. 🔍 Automated PR Code & Security Review

Every Pull Request can trigger an automated review.

### Workflow

```text
Pull Request
      ↓
GitHub Actions
      ↓
Lint + Tests + Trivy + SonarQube
      ↓
Unified Diff + Security Results
      ↓
AI Analysis
      ↓
PR Review + Suggested Fixes
```

### Features

* PR diff analysis
* Code-quality review
* Security vulnerability detection
* Trivy integration
* SonarQube integration
* AI-generated review summary
* Risk classification
* Suggested code changes
* GitHub PR comments
* GitHub suggestion blocks

The system supports `opened`, `synchronize`, and `reopened` Pull Request events.

---

## 2. 🚨 Intelligent CI/CD Failure Diagnoser

When a GitHub Actions workflow fails, the assistant can analyze the failure automatically.

### Workflow

```text
GitHub Actions Failure
        ↓
Build Logs
        ↓
Failure / Stack Trace Extraction
        ↓
AI Analysis
        ↓
Root Cause
        ↓
Suggested Fix / Patch
```

### Capabilities

* Reads CI/CD build logs
* Identifies the failing step
* Extracts relevant errors
* Explains failures in plain English
* Identifies probable root causes
* Generates code or configuration patches
* Helps developers debug faster

The system is designed around `workflow_run.conclusion == 'failure'` events.

---

# 3. 🚀 GitOps Deployment with ArgoCD

After a Pull Request is merged into `main`, the deployment pipeline can automatically promote the application.

### Deployment Flow

```text
PR Merged
    ↓
GitHub Actions
    ↓
Docker Build
    ↓
Amazon ECR
    ↓
GitOps Manifest Update
    ↓
ArgoCD Sync
    ↓
AWS EKS
    ↓
Rolling Deployment
```

### Deployment Process

1. Build a multi-architecture Docker image.
2. Tag the image using the commit SHA.
3. Push the image to Amazon ECR.
4. Update the GitOps repository.
5. Trigger ArgoCD synchronization.
6. Deploy the new version to AWS EKS.
7. Post deployment confirmation back to GitHub.

---

# 4. ☁️ AWS Infrastructure with Terraform

Infrastructure is provisioned using Terraform.

### Infrastructure Includes

* AWS VPC
* Public and private subnets
* NAT Gateways
* Amazon EKS
* Managed node groups
* IAM roles
* OIDC / IRSA
* Amazon ECR
* ArgoCD
* Prometheus
* Grafana
* Kubernetes monitoring

The project configuration specifies a Multi-AZ VPC with 3 public and 3 private subnets and Terraform-managed EKS/ECR infrastructure.

---

# 5. 📊 Monitoring & Observability

The system exposes application metrics for Prometheus and visualization through Grafana.

### Monitoring Stack

```text
Application
     ↓
Prometheus Metrics
     ↓
Prometheus
     ↓
Grafana
     ↓
Dashboards + Alerts
```

Tracked metrics include:

* Request latency
* PR review counters
* GitOps synchronization counters
* Application health
* Kubernetes metrics
* Service availability

---

# 6. 🖥️ Real-Time Operations Dashboard

The project includes a modern operations dashboard for interacting with and testing the system.

### Dashboard Features

* Live system status
* LLM health indicator
* ArgoCD sync status
* EKS connectivity status
* PR Review Studio
* CI/CD Failure Diagnoser
* Webhook Simulator
* Live event feed
* GitOps monitoring
* Security scan results

---

# 🎬 Live Application Showcase

The AI DevOps Assistant includes a live interactive operations console demonstrating:

* Automated PR reviews
* CI/CD failure root-cause analysis
* GitOps event simulation
* Deployment monitoring
* Webhook events

> **Local application:** `http://127.0.0.1:8000`

## 📸 Feature Walkthrough

### Operations Dashboard

![Operations Dashboard & Status Indicators](./screenshots/initial_page_load.png)

### PR Code & Security Review

![PR Code & Security Review Studio Results](./screenshots/pr_review_results.png)

### CI/CD Failure Diagnosis

![CI/CD Build Failure Diagnosis & Fix Patch](./screenshots/cicd_diagnosis_results.png)

### Webhook Event Simulator

![Live Webhook Event Simulator & Audit Stream](./screenshots/all_simulated_events.png)

### GitOps / ArgoCD Monitor

![GitOps & ArgoCD Kubernetes Sync Monitor](./screenshots/gitops_tab_clean.png)

> **Important:** Place the five screenshot files inside a `screenshots/` folder in your repository and keep the filenames exactly as referenced above.

---

# 🛠️ API Endpoints

| Capability         | Endpoint                     | Description                 |
| ------------------ | ---------------------------- | --------------------------- |
| 🖥️ Dashboard      | `GET /`                      | Operations dashboard        |
| 🔍 PR Review       | `POST /api/analyze-pr`       | Diff + security analysis    |
| 🚨 CI/CD Diagnosis | `POST /api/diagnose-failure` | Failure root-cause analysis |
| 🔗 GitHub Webhook  | `POST /webhook`              | GitHub event receiver       |
| 🚀 GitOps Sync     | `POST /api/gitops/sync`      | ArgoCD deployment trigger   |
| ❤️ Health Check    | `GET /healthz`               | Health/readiness check      |
| 📊 Metrics         | `GET /metrics`               | Prometheus metrics          |

These endpoints are documented by the project showcase.

---

# 📂 Project Structure

```text
ai-devops-assistant/
│
├── .github/
│   └── workflows/
│       ├── pr-security-and-ai-review.yml
│       ├── pipeline-failure-reporter.yml
│       └── ci-cd-on-merge.yml
│
├── app/
│   ├── config.py
│   ├── main.py
│   │
│   ├── routers/
│   │   ├── api.py
│   │   └── webhooks.py
│   │
│   ├── services/
│   │   ├── github_service.py
│   │   ├── gitops_service.py
│   │   └── llm_engine.py
│   │
│   └── static/
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   └── app.js
│       └── index.html
│
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── monitoring/
│       └── servicemonitor.yaml
│
├── argocd/
│   └── application.yaml
│
├── terraform/
│   ├── main.tf
│   ├── vpc.tf
│   ├── eks.tf
│   ├── ecr.tf
│   ├── argocd.tf
│   ├── monitoring.tf
│   ├── variables.tf
│   └── outputs.tf
│
├── tests/
│   ├── test_api.py
│   ├── test_llm_engine.py
│   └── test_webhook.py
│
├── screenshots/
│   ├── initial_page_load.png
│   ├── pr_review_results.png
│   ├── cicd_diagnosis_results.png
│   ├── all_simulated_events.png
│   └── gitops_tab_clean.png
│
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

# 🚀 Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-devops-assistant.git
cd ai-devops-assistant
```

---

## 2. Create a Virtual Environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Configuration

Create a `.env` file:

```env
# LLM Provider
LLM_PROVIDER=gemini

# Gemini
GEMINI_API_KEY=your-gemini-api-key

# Optional OpenAI
# OPENAI_API_KEY=your-openai-api-key

# GitHub App
GITHUB_APP_ID=123456
GITHUB_WEBHOOK_SECRET=your-webhook-secret

# Optional GitHub OAuth
# GITHUB_CLIENT_ID=your-client-id
# GITHUB_CLIENT_SECRET=your-client-secret
# GITHUB_REDIRECT_URI=http://localhost:8000/auth/github/callback

# GitHub App Private Key
# GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n..."

# ArgoCD
ARGOCD_SERVER_URL=https://your-argocd-server
ARGOCD_AUTH_TOKEN=your-argocd-token
```

The original project supports Gemini, OpenAI, and a high-fidelity mock LLM engine for local testing.

> **Security:** Never commit `.env`, API keys, GitHub private keys, or ArgoCD tokens to GitHub.

Add this to `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.pem
*.key
```

---

# ▶️ Run the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open:

```text
http://localhost:8000
```

The dashboard provides:

* PR Review Studio
* CI/CD Failure Diagnoser
* Live Events & Simulator

---

# 📚 API Documentation

FastAPI automatically provides Swagger documentation.

Open:

```text
http://localhost:8000/docs
```

Other useful endpoints:

```text
http://localhost:8000/
http://localhost:8000/docs
http://localhost:8000/metrics
http://localhost:8000/healthz
```

---

# 🧪 Run Tests

Run the complete test suite:

```bash
pytest tests/ -v
```

The project includes tests for:

* FastAPI endpoints
* LLM analysis
* GitHub webhook validation

---

# 🐳 Docker Compose

Run the complete local stack:

```bash
docker-compose up --build -d
```

Services:

| Service                | URL                     |
| ---------------------- | ----------------------- |
| 🤖 Assistant Dashboard | `http://localhost:8000` |
| 📊 Prometheus          | `http://localhost:9090` |
| 📈 Grafana             | `http://localhost:3000` |

Default Grafana credentials:

```text
Username: admin
Password: admin
```

---

# ☁️ Deploy to AWS

The project uses Terraform to provision AWS infrastructure.

## Initialize Terraform

```bash
cd terraform

terraform init
```

## Review Infrastructure

```bash
terraform plan -out=tfplan
```

## Apply Infrastructure

```bash
terraform apply tfplan
```

This provisions the AWS infrastructure required for:

* VPC
* EKS
* ECR
* ArgoCD
* Prometheus
* Grafana

---

# ☸️ Deploy to Kubernetes

After the infrastructure is available:

```bash
kubectl apply -f ../k8s/
```

Deploy the ArgoCD application:

```bash
kubectl apply -f ../argocd/application.yaml
```

---

# 🔗 GitHub App Setup

Create a GitHub App:

```text
GitHub
 → Settings
 → Developer Settings
 → GitHub Apps
 → New GitHub App
```

Configure the webhook:

```text
https://<YOUR_INGRESS_DOMAIN>/webhook/github
```

Set the webhook secret to match:

```env
GITHUB_WEBHOOK_SECRET=your-webhook-secret
```

### Required Repository Permissions

| Permission       | Access       |
| ---------------- | ------------ |
| Pull Requests    | Read & Write |
| Actions / Checks | Read         |
| Contents         | Read         |
| Issues           | Read & Write |

### Subscribe to Events

* Pull request
* Workflow run
* Issue comment

Store the GitHub App private key securely.

---

# 🔄 Complete DevOps Workflow

The complete automated workflow looks like this:

```text
                    ┌─────────────────┐
                    │     Developer   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Pull Request  │
                    └────────┬────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │    GitHub Actions     │
                 │ Lint + Test + Security│
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │   AI DevOps Assistant │
                 │                       │
                 │ • PR Review           │
                 │ • Security Analysis   │
                 │ • Failure Diagnosis  │
                 └───────────┬───────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   GitHub PR     │
                    │ Comments/Fixes  │
                    └────────┬────────┘
                             │
                          Merge
                             │
                             ▼
                    ┌─────────────────┐
                    │ Docker Build    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Amazon ECR    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    ArgoCD       │
                    │  GitOps Sync    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    AWS EKS      │
                    │   Kubernetes    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Prometheus +    │
                    │ Grafana         │
                    └─────────────────┘
```

---

# 🧠 AI Components

The AI layer can use:

* Google Gemini
* OpenAI
* Mock LLM engine for development

The LLM is used for:

### PR Analysis

```text
Git Diff
   +
Security Scan Results
   ↓
LLM
   ↓
Summary
Risk
Issues
Suggestions
```

### CI/CD Diagnosis

```text
Build Logs
   ↓
Error Extraction
   ↓
LLM
   ↓
Root Cause
   ↓
Recommended Fix
```

---

# 🔐 Security

The application includes several security-oriented components:

* GitHub webhook HMAC-SHA256 verification
* Trivy vulnerability scanning
* SonarQube analysis
* Kubernetes security contexts
* AWS IAM / IRSA
* ECR image scanning
* Environment-based secrets
* GitHub App authentication

Never commit production credentials or private keys to the repository.

---

# 📈 Observability

Prometheus metrics are exposed through:

```text
GET /metrics
```

Health checks are available through:

```text
GET /healthz
```

These can be consumed by Kubernetes monitoring and Grafana dashboards.

---

# 🤝 Contributing

Contributions are welcome!

If you have an idea, bug fix, improvement, security enhancement, or new feature that can make the **AI-Powered DevOps Assistant** better, feel free to contribute through a Pull Request.

## 🚀 How to Contribute

### 1. Fork the Repository

Click the **Fork** button at the top-right of this GitHub repository.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/ai-devops-assistant.git
cd ai-devops-assistant
```

### 3. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 4. Make Your Changes

Implement your feature, bug fix, documentation update, or improvement.

### 5. Run Tests

```bash
pytest tests/ -v
```

Make sure existing functionality continues to work.

### 6. Commit Your Changes

```bash
git add .
git commit -m "feat: add your feature"
```

### 7. Push Your Branch

```bash
git push origin feature/your-feature-name
```

### 8. Open a Pull Request

Go to your GitHub fork and create a Pull Request against the main repository.

---

# 📋 Contribution Guidelines

Before submitting a Pull Request:

* Keep changes focused and understandable.
* Follow the existing project structure.
* Add tests for new functionality where appropriate.
* Update documentation when adding new features.
* Do not commit secrets or credentials.
* Ensure the application still starts successfully.
* Run the test suite before opening a PR.

---

# 🗺️ Future Improvements

Potential future enhancements include:

* Multi-repository GitHub App support
* More LLM providers
* Automatic issue creation
* Slack / Discord notifications
* Advanced security scanning
* AI-generated incident reports
* Automatic rollback detection
* Cost monitoring
* Advanced Grafana dashboards
* Kubernetes anomaly detection
* AI-powered infrastructure recommendations
* Multi-cloud deployment support

---

# ⭐ Why This Project?

This project brings together multiple modern engineering domains:

```text
AI / LLM
   +
Python / FastAPI
   +
GitHub Actions
   +
Docker
   +
Kubernetes
   +
AWS
   +
Terraform
   +
ArgoCD
   +
Prometheus
   +
Grafana
```

Instead of building an isolated AI application, the **AI DevOps Assistant** demonstrates how AI can be integrated into a real software delivery lifecycle.

---

# 📜 License

This project is available under the **MIT License**.

---

# 👨‍💻 Author

**Harshit Agrahari**

* GitHub: `Harshit4grahari`
* LinkedIn: `harshit-agrahari-5621a0299`

---

## ⭐ If You Like This Project

Give the repository a ⭐ on GitHub and feel free to contribute!

Built with ❤️ using **AI + DevOps + Cloud + Kubernetes + GitOps**.
