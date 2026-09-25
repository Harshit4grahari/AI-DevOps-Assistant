# ⚡ AI-Powered DevOps Assistant

An enterprise-grade GitHub App, CI/CD Guardian, and GitOps Automation Engine. It integrates directly into any repository's pipeline to provide **automated PR code & security reviews**, **intelligent CI/CD build failure diagnosis**, and **zero-downtime GitOps deployments via ArgoCD to AWS EKS**, all provisioned with **Terraform** and monitored via **Prometheus + Grafana**.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph GitHub["GitHub Ecosystem"]
        PR[Pull Request Opened / Synchronized]
        GHA[GitHub Actions: Lint, Test, Trivy, SonarQube]
        Merge[PR Merged into main]
        Fail[Workflow Run Failure]
    end

    subgraph DevOpsBot["AI DevOps Assistant Service (FastAPI)"]
        WH[Webhook & Event Gateway]
        LLM[LLM Engine: Gemini / OpenAI]
        PRReviewer[PR Diff & Security Scan Analyzer]
        LogAnalyzer[CI/CD Failure Diagnostic Engine]
        GitOpsSync[GitOps & ArgoCD Orchestrator]
        Dashboard[Modern Operations Dashboard & Simulator]
    end

    subgraph GitOpsK8s["GitOps & Kubernetes (AWS EKS)"]
        ECR[Amazon ECR Container Registry]
        ArgoCD[ArgoCD GitOps Controller]
        K8sCluster[EKS Workloads & Services]
    end

    subgraph MonitoringInfra["AWS Infra & Observability (Terraform)"]
        TF[Terraform: VPC, EKS, ECR, IAM]
        Prom[Prometheus Metrics]
        Graf[Grafana Dashboards & Alerts]
    end

    PR -->|Webhook / Action| WH
    GHA -->|SARIF/JSON + Diffs| PRReviewer
    PRReviewer --> LLM
    LLM -->|Formatted PR Review + Suggestions| PR

    Fail -->|Workflow Run Failure / Logs| LogAnalyzer
    LogAnalyzer --> LLM
    LLM -->|Root Cause Analysis & Fix Patch| PR

    Merge -->|CI/CD on Merge| ECR
    ECR --> GitOpsSync
    GitOpsSync -->|Image Tag Promotion| ArgoCD
    ArgoCD -->|Sync & Deploy| K8sCluster

    TF --> K8sCluster
    K8sCluster --> Prom
    Prom --> Graf
    WH --> Dashboard
```

---

## 🌟 Key Capabilities

### 1. 🔍 Automated PR Code & Security Review
- **Triggered On**: Every Pull Request (`opened`, `synchronize`, `reopened`).
- **Pipeline Scans**: Integrates **Trivy** (container vulnerabilities, OS CVEs, misconfigurations) and **SonarQube** (code smells, bugs, security hotspots).
- **AI Synthesis**: Combines the unified diff + security scan outputs into an executive summary, risk rating (Low/Medium/High/Critical), and **one-click GitHub suggestion diff blocks** (` ```suggestion `).

### 2. 🚨 Intelligent CI/CD Failure Diagnoser
- **Triggered On**: Any failed GitHub Actions workflow run (`workflow_run.conclusion == 'failure'`).
- **Root Cause Isolation**: Ingests raw build logs, isolates failing stack traces, explains the failure in plain language, and generates an exact code, command, or workflow patch.

### 3. 🚀 Zero-Downtime GitOps Deployments (ArgoCD on Merge)
- **Triggered On**: PR merged into `main`.
- **Workflow**:
  1. GitHub Actions builds multi-arch Docker image tagged with commit SHA.
  2. Pushes image to Amazon ECR.
  3. Updates the target GitOps manifest repository (Kustomize/Helm values).
  4. Triggers ArgoCD application sync for zero-downtime rolling update on AWS EKS.
  5. Posts deployment confirmation comment to the PR.

### 4. ☁️ Production AWS Infrastructure (Terraform)
- **Multi-AZ VPC**: 3 Public + 3 Private subnets with NAT Gateways.
- **Amazon EKS Cluster**: Managed node groups, IAM Roles for Service Accounts (IRSA), OIDC provider.
- **Amazon ECR**: Container registry with scan-on-push and automated lifecycle retention policies.
- **ArgoCD & Prometheus Stack**: Bootstrapped via Terraform Helm provider with Alertmanager and Grafana dashboards.

### 5. 🖥️ Real-Time Operations Dashboard & Simulator
- **Live Status Badges**: LLM health, ArgoCD sync state, EKS connectivity.
- **PR Review Studio**: Test arbitrary diffs and Trivy/SonarQube reports with instant markdown rendering.
- **CI/CD Failure Console**: Test raw error logs and view isolated root causes.
- **Webhook Simulator**: Test GitHub webhook events (`pull_request`, `workflow_run`) with live feed updates.

---

## 📂 Project Structure

```
ai-devops-assistant/
├── .github/workflows/
│   ├── pr-security-and-ai-review.yml    # Lint, test, Trivy, SonarQube, AI PR review
│   ├── pipeline-failure-reporter.yml    # Build failure log extractor & AI diagnostic
│   └── ci-cd-on-merge.yml               # Docker build, ECR push, GitOps ArgoCD sync
├── app/
│   ├── config.py                        # Pydantic Settings & environment variables
│   ├── main.py                          # FastAPI server, metrics middleware, static routes
│   ├── routers/
│   │   ├── api.py                       # REST API & simulator endpoints
│   │   └── webhooks.py                  # GitHub webhook receiver (HMAC signature verification)
│   ├── services/
│   │   ├── github_service.py            # GitHub App JWT, diff fetching, comments, logs
│   │   ├── gitops_service.py            # ArgoCD sync & manifest patch generator
│   │   └── llm_engine.py                # Multi-provider LLM (Gemini, OpenAI, Mock)
│   └── static/
│       ├── css/style.css                # Modern dark-mode styling & glassmorphism
│       ├── js/app.js                    # Interactive dashboard logic & simulator
│       └── index.html                   # Dashboard UI
├── k8s/
│   ├── deployment.yaml                  # Kubernetes Deployment with health probes & securityContext
│   ├── service.yaml                     # Service, Ingress (AWS ALB), and HPA
│   └── monitoring/
│       └── servicemonitor.yaml          # Prometheus ServiceMonitor & PrometheusRule alerts
├── argocd/
│   └── application.yaml                 # ArgoCD Application CRD for automated GitOps
├── terraform/
│   ├── main.tf                          # Providers (AWS, K8s, Helm)
│   ├── vpc.tf                           # Multi-AZ VPC with NAT Gateways
│   ├── eks.tf                           # Amazon EKS cluster & node groups
│   ├── ecr.tf                           # Amazon ECR with lifecycle rules
│   ├── argocd.tf                        # Helm release for ArgoCD
│   ├── monitoring.tf                    # Helm release for kube-prometheus-stack (Grafana)
│   ├── variables.tf                     # Input variables
│   └── outputs.tf                       # Cluster endpoints, ECR URLs, ArgoCD URL
├── tests/
│   ├── test_api.py                      # FastAPI endpoint tests
│   ├── test_llm_engine.py               # Diff & log analysis unit tests
│   └── test_webhook.py                  # Webhook signature & event tests
├── Dockerfile                           # Production multi-stage Dockerfile
├── docker-compose.yml                   # Local development stack (App + Prom + Grafana)
└── requirements.txt                     # Python dependencies
```

---

## 🚀 Getting Started

### 1. Local Development Setup

1. **Clone and create a virtual environment**:
   ```powershell
   cd C:\Users\agrah\.gemini\antigravity-ide\scratch\ai-devops-assistant
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables** (Optional - works out of the box with high-fidelity mock engine):
   Create a `.env` file:
   ```env
   # LLM Provider (choose 'gemini' or 'openai' or 'mock')
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your-gemini-api-key
   # OPENAI_API_KEY=your-openai-api-key

   # GitHub App Configuration (Optional for local testing)
   GITHUB_APP_ID=123456
   GITHUB_WEBHOOK_SECRET=devops-assistant-webhook-secret
   # GitHub OAuth App configuration
   # GITHUB_CLIENT_ID=your-github-oauth-client-id
   # GITHUB_CLIENT_SECRET=your-github-oauth-client-secret
   # GITHUB_REDIRECT_URI=http://localhost:8000/auth/github/callback
   # GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n..."

   # ArgoCD & GitOps
   ARGOCD_SERVER_URL=https://argocd.internal.infra
   ARGOCD_AUTH_TOKEN=your-argocd-token
   ```

3. **Run the Assistant Server**:
   ```powershell
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access the Dashboard**:
   Open [http://localhost:8000](http://localhost:8000) in your browser.
   - Test PR reviews using the **PR Review Studio** tab.
   - Test build failure diagnosis using the **CI/CD Failure Diagnoser** tab.
   - Simulate webhook events using the **Live Events & Simulator** tab.

---

### 2. Running Automated Tests

Run the test suite with `pytest`:
```powershell
pytest tests/ -v
```

---

### 3. Running with Docker Compose

Run the full local observability and assistant stack:
```powershell
docker-compose up --build -d
```
- **Assistant Dashboard**: [http://localhost:8000](http://localhost:8000)
- **Prometheus Metrics**: [http://localhost:9090](http://localhost:9090)
- **Grafana Dashboard**: [http://localhost:3000](http://localhost:3000) (User: `admin`, Pass: `admin`)

---

### 4. Deploying to AWS via Terraform

1. **Initialize and Review Plan**:
   ```powershell
   cd terraform
   terraform init
   terraform plan -out=tfplan
   ```

2. **Apply Infrastructure**:
   ```powershell
   terraform apply tfplan
   ```
   This provisions:
   - AWS VPC with public and private subnets.
   - Amazon EKS cluster with 3 worker nodes.
   - Amazon ECR repository for container images.
   - ArgoCD server running in `argocd` namespace.
   - Prometheus Operator & Grafana in `monitoring` namespace.

3. **Deploy the Assistant into EKS**:
   ```powershell
   kubectl apply -f ../k8s/
   kubectl apply -f ../argocd/application.yaml
   ```

---

## 🔐 GitHub App Registration & Webhook Setup

1. Go to **GitHub Settings > Developer Settings > GitHub Apps > New GitHub App**.
2. Set **Webhook URL** to: `https://<YOUR_INGRESS_DOMAIN>/webhook/github`.
3. Set **Webhook Secret** matching `GITHUB_WEBHOOK_SECRET`.
4. Configure Repository Permissions:
   - **Pull requests**: Read & Write
   - **Actions / Checks**: Read
   - **Contents**: Read
   - **Issues**: Read & Write
5. Subscribe to events: `Pull request`, `Workflow run`, `Issue comment`.
6. Download the private key (`.pem`) and store it securely.


## 🤝 Contributing

Contributions are welcome! If you have an idea, bug fix, improvement, or new feature that can make the **AI-Powered DevOps Assistant** better, feel free to contribute through a Pull Request.

### 🚀 How to Contribute

1. **Fork this repository**

   * Click the **Fork** button at the top-right of this GitHub repository.

2. **Clone your fork**

   ```bash
   git clone https://github.com/YOUR-USERNAME/ai-devops-assistant.git
   cd ai-devops-assistant
   ```

3. **Create a new branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make your changes**

   * Add your feature, fix a bug, improve documentation, tests, UI, CI/CD workflows, or infrastructure.
   * Keep changes focused and follow the existing project structure and coding style.

5. **Run the tests**

   ```bash
   pytest tests/ -v
   ```

6. **Commit your changes**

   ```bash
   git add .
   git commit -m "feat: add your feature"
   ```

7. **Push your branch**

   ```bash
   git push origin feature/your-feature-name
   ```

8. **Open a Pull Request**

   * Go to your fork on GitHub.
   * Click **Compare & pull request**.
   * Clearly describe what you changed and why.
   * Include screenshots, logs, or test results when useful.
   * Submit the Pull Request for review.

### ✅ Pull Request Guidelines

Before submitting a PR, please make sure:

* [ ] The project still runs locally.
* [ ] Existing tests pass.
* [ ] New functionality includes appropriate tests where applicable.
* [ ] No API keys, passwords, private keys, tokens, or other secrets are committed.
* [ ] Documentation is updated when necessary.
* [ ] The PR has a clear title and description.
* [ ] Changes are focused on the purpose of the PR.

### 💡 What You Can Contribute

You can contribute to areas such as:

* 🤖 AI/LLM code review and failure diagnosis
* 🔐 Security scanning and DevSecOps integrations
* 🐙 GitHub App and webhook integrations
* ⚙️ GitHub Actions and CI/CD workflows
* 🐳 Docker and containerization
* ☸️ Kubernetes and ArgoCD
* ☁️ AWS and Terraform infrastructure
* 📊 Prometheus/Grafana monitoring
* 🖥️ Dashboard/UI improvements
* 🧪 Automated tests
* 📚 Documentation and examples
* 🐛 Bug fixes and performance improvements

If you are unsure about a change, open an **Issue** first to discuss the idea before starting a large implementation.

**Thank you for contributing! 🚀**

