# ⚡ AI DevOps Assistant — Live Application Showcase

The **AI DevOps Assistant** is running live at **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.

---

## 🎬 Live Interactive Session Recording

Here is the full recorded walkthrough of the interactive operations console, demonstrating automated PR reviews, CI/CD failure root-cause analysis, and GitOps event simulation:

![Live Interactive Browser Session](C:/Users/agrah/.gemini/antigravity-ide/brain/8ba953c8-e011-42ac-90ac-4161c3e15059/dashboard_demo_1790266395052.webp)

---

## 📸 Feature Walkthrough & Screenshots

````carousel
![Operations Dashboard & Status Indicators](C:/Users/agrah/.gemini/antigravity-ide/brain/8ba953c8-e011-42ac-90ac-4161c3e15059/initial_page_load_1790266460868.png)
<!-- slide -->
![PR Code & Security Review Studio Results](C:/Users/agrah/.gemini/antigravity-ide/brain/8ba953c8-e011-42ac-90ac-4161c3e15059/pr_review_results_1790266568547.png)
<!-- slide -->
![CI/CD Build Failure Diagnosis & Fix Patch](C:/Users/agrah/.gemini/antigravity-ide/brain/8ba953c8-e011-42ac-90ac-4161c3e15059/cicd_diagnosis_results_1790267085966.png)
<!-- slide -->
![Live Webhook Event Simulator & Audit Stream](C:/Users/agrah/.gemini/antigravity-ide/brain/8ba953c8-e011-42ac-90ac-4161c3e15059/all_simulated_events_1790268494060.png)
<!-- slide -->
![GitOps & ArgoCD Kubernetes Sync Monitor](C:/Users/agrah/.gemini/antigravity-ide/brain/8ba953c8-e011-42ac-90ac-4161c3e15059/gitops_tab_clean_1790269197015.png)
````

---

## 🛠️ Key Capabilities & Endpoints

| Capability | Module / Endpoint | Description |
| :--- | :--- | :--- |
| **Dashboard UI** | `GET /` | Modern operations cockpit with dark glassmorphism theme |
| **PR Review Engine** | `POST /api/analyze-pr` | Unified diff analysis + Trivy & SonarQube vulnerability scanning |
| **CI/CD Diagnoser** | `POST /api/diagnose-failure` | Plain-language failure root cause isolation + diff patches |
| **Webhook Gateway** | `POST /webhook` | Receives GitHub events (`pull_request`, `workflow_run`) with HMAC-SHA256 verification |
| **GitOps Sync** | `POST /api/gitops/sync` | ArgoCD application trigger & automated image tag updates |
| **Kubernetes Probe** | `GET /healthz` | Cluster readiness and liveness health checks |
| **Prometheus Scrape** | `GET /metrics` | Exposes latency histograms, PR counters, and sync counters |

---

## 🌐 How to Access Locally

1. **Dashboard UI**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
2. **Interactive OpenAPI / Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
3. **Prometheus Metrics**: [http://127.0.0.1:8000/metrics](http://127.0.0.1:8000/metrics)
4. **Health Check**: [http://127.0.0.1:8000/healthz](http://127.0.0.1:8000/healthz)
