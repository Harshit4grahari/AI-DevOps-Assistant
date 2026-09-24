/* ==========================================================================
   AI DevOps Assistant Client-Side Controller
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initAuth();
  initRepoManager();
  initStatusPolling();
  initEventFeed();
  initPRReviewStudio();
  initLogDiagnoser();
  initWebhookSimulator();
  initGitOpsActions();
});

/* Tab Switching */
function initTabs() {
  const buttons = document.querySelectorAll(".tab-button");
  const contents = document.querySelectorAll(".tab-content");

  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetTab = btn.dataset.tab;

      buttons.forEach((b) => b.classList.remove("active"));
      contents.forEach((c) => c.classList.remove("active"));

      btn.classList.add("active");
      const activeContent = document.getElementById(targetTab);
      if (activeContent) activeContent.classList.add("active");
    });
  });
}

/* Status and Metrics */
async function initStatusPolling() {
  const updateStatus = async () => {
    try {
      const res = await fetch("/api/status");
      if (res.ok) {
        const data = await res.json();
        const llmBadge = document.getElementById("status-llm");
        const argoBadge = document.getElementById("status-argo");

        if (llmBadge) {
          llmBadge.textContent = `LLM: ${data.llm_provider.toUpperCase()} (${data.llm_configured ? "Active" : "Simulated/Mock"})`;
        }
        if (argoBadge) {
          argoBadge.textContent = `ArgoCD: ${data.argocd_health}`;
        }
      }
    } catch (err) {
      console.warn("Status poll error:", err);
    }
  };

  updateStatus();
  setInterval(updateStatus, 15000);
}

/* Event Feed */
async function initEventFeed() {
  const feedContainer = document.getElementById("event-feed-container");
  const loadEvents = async () => {
    try {
      const res = await fetch("/api/events");
      if (res.ok) {
        const events = await res.json();
        if (!feedContainer) return;

        if (events.length === 0) {
          feedContainer.innerHTML = `
            <div class="output-placeholder">
              <span>📡</span>
              <p>No webhook events received yet.<br>Use the simulator or send GitHub webhooks to populate this feed.</p>
            </div>
          `;
          return;
        }

        feedContainer.innerHTML = events
          .map((e) => {
            const isPR = e.type === "pull_request";
            const isMerged = isPR && e.action === "closed";
            const isFail = e.type === "workflow_run" && e.conclusion === "failure";

            let icon = isPR ? "🔀" : "⚙️";
            let badgeClass = "badge-primary";
            let title = isPR ? `PR #${e.pr_number}: ${e.title || "Code Review"}` : `Workflow: ${e.workflow || "CI Pipeline"}`;

            if (isMerged) {
              icon = "🚀";
              badgeClass = "badge-success";
              title = `PR #${e.pr_number} Merged -> GitOps Sync Triggered`;
            } else if (isFail) {
              icon = "🚨";
              badgeClass = "badge-danger";
              title = `Pipeline Failure Diagnosed in ${e.repo || "repo"}`;
            }

            return `
              <div class="event-card">
                <div class="event-icon" style="background: rgba(99, 102, 241, 0.15)">${icon}</div>
                <div class="event-details" style="flex: 1;">
                  <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4>${escapeHtml(title)}</h4>
                    <span class="badge ${badgeClass}">${escapeHtml(e.status || "processed")}</span>
                  </div>
                  <p>${escapeHtml(e.details || "Event processed through AI DevOps Assistant")}</p>
                  <div class="event-meta">Repo: <code>${escapeHtml(e.repo || "repo")}</code> • Action: <code>${escapeHtml(e.action || "webhook")}</code></div>
                </div>
              </div>
            `;
          })
          .join("");
      }
    } catch (err) {
      console.warn("Event feed error:", err);
    }
  };

  loadEvents();
  setInterval(loadEvents, 5000);
}

/* PR Review Studio */
function initPRReviewStudio() {
  const btn = document.getElementById("btn-run-pr-review");
  const output = document.getElementById("pr-review-output");
  const diffInput = document.getElementById("pr-diff-input");
  const trivyInput = document.getElementById("pr-trivy-input");
  const titleInput = document.getElementById("pr-title-input");
  const prUrlInput = document.getElementById("pr-url-input");
  const btnFetchPr = document.getElementById("btn-fetch-pr");
  const fetchStatus = document.getElementById("fetch-pr-status");

  // Fetch PR by URL handler
  if (btnFetchPr && prUrlInput) {
    btnFetchPr.addEventListener("click", async () => {
      const url = prUrlInput.value.trim();
      if (!url) {
        alert("Please enter a valid GitHub PR URL (e.g. https://github.com/owner/repo/pull/123)");
        return;
      }

      btnFetchPr.disabled = true;
      btnFetchPr.textContent = "⏳ Fetching...";
      if (fetchStatus) {
        fetchStatus.style.display = "block";
        fetchStatus.style.color = "#94a3b8";
        fetchStatus.textContent = "Fetching PR diff and metadata from GitHub...";
      }

      try {
        const res = await fetch("/api/fetch-pr", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ pr_url: url }),
        });
        const data = await res.json();

        if (res.ok && data.status === "success") {
          if (titleInput && data.title) titleInput.value = data.title;
          if (diffInput && data.diff) diffInput.value = data.diff;
          if (fetchStatus) {
            fetchStatus.style.color = "#10b981";
            fetchStatus.textContent = `✅ Successfully imported ${data.repo} #${data.pr_number}! Ready for review.`;
          }
        } else {
          if (fetchStatus) {
            fetchStatus.style.color = "#ef4444";
            fetchStatus.textContent = `❌ ${data.message || "Failed to fetch PR. Ensure URL is correct."}`;
          }
        }
      } catch (err) {
        if (fetchStatus) {
          fetchStatus.style.color = "#ef4444";
          fetchStatus.textContent = `❌ Error: ${err.message}`;
        }
      } finally {
        btnFetchPr.disabled = false;
        btnFetchPr.textContent = "📥 Fetch PR";
      }
    });
  }

  btn.addEventListener("click", async () => {
    btn.disabled = true;
    btn.innerHTML = `⏳ Analyzing Diff & Security Scans...`;
    output.innerHTML = `
      <div class="output-placeholder">
        <span>🤖</span>
        <p>AI Assistant is inspecting unified diff, running AST checks, and synthesizing Trivy CVEs...</p>
      </div>
    `;

    try {
      const payload = {
        title: titleInput.value || "Pull Request",
        diff: diffInput.value,
        trivy_report: trivyInput.value || null,
        description: "Pull request submitted for automated review.",
      };

      const res = await fetch("/api/analyze/diff", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (res.ok && data.markdown_review) {
        output.innerHTML = `<div class="markdown-body">${renderMarkdown(data.markdown_review)}</div>`;
        incrementMetric("metric-prs-reviewed");
      } else {
        output.innerHTML = `<p style="color: var(--danger)">Error running analysis: ${escapeHtml(data.detail || "Unknown error")}</p>`;
      }
    } catch (err) {
      output.innerHTML = `<p style="color: var(--danger)">Request failed: ${escapeHtml(err.message)}</p>`;
    } finally {
      btn.disabled = false;
      btn.innerHTML = `🚀 Run AI Code & Security Review`;
    }
  });
}

/* CI/CD Log Diagnoser */
function initLogDiagnoser() {
  const btn = document.getElementById("btn-run-diagnose");
  const output = document.getElementById("log-diagnosis-output");
  const logsInput = document.getElementById("log-text-input");
  const workflowInput = document.getElementById("log-workflow-input");

  if (!btn || !output) return;

  btn.addEventListener("click", async () => {
    btn.disabled = true;
    btn.innerHTML = `⏳ Diagnosing Failure Logs...`;
    output.innerHTML = `
      <div class="output-placeholder">
        <span>🔬</span>
        <p>Isolating stack trace, parsing exit codes, and generating code patch...</p>
      </div>
    `;

    try {
      const payload = {
        workflow_name: workflowInput.value || "CI Workflow",
        logs: logsInput.value,
        failed_step: "Automated Testing",
      };

      const res = await fetch("/api/analyze/logs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (res.ok && data.markdown_diagnosis) {
        output.innerHTML = `<div class="markdown-body">${renderMarkdown(data.markdown_diagnosis)}</div>`;
        incrementMetric("metric-failures-diagnosed");
      } else {
        output.innerHTML = `<p style="color: var(--danger)">Error: ${escapeHtml(data.detail || "Diagnosis failed")}</p>`;
      }
    } catch (err) {
      output.innerHTML = `<p style="color: var(--danger)">Request failed: ${escapeHtml(err.message)}</p>`;
    } finally {
      btn.disabled = false;
      btn.innerHTML = `🔍 Diagnose Build Failure`;
    }
  });
}

/* Webhook Simulator */
function initWebhookSimulator() {
  const btnSimulatePR = document.getElementById("btn-sim-pr");
  const btnSimulateMerge = document.getElementById("btn-sim-merge");
  const btnSimulateFail = document.getElementById("btn-sim-fail");

  const triggerSim = async (eventType, action) => {
    try {
      await fetch("/api/simulate-webhook", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          event_type: eventType,
          action: action,
          repo_name: "acme-corp/cloud-backend",
          pr_number: Math.floor(Math.random() * 800) + 100,
        }),
      });
      // Switch to events tab
      const feedTabBtn = document.querySelector('[data-tab="tab-feed"]');
      if (feedTabBtn) feedTabBtn.click();
    } catch (e) {
      console.error(e);
    }
  };

  if (btnSimulatePR) btnSimulatePR.addEventListener("click", () => triggerSim("pull_request", "opened"));
  if (btnSimulateMerge) btnSimulateMerge.addEventListener("click", () => triggerSim("pull_request", "closed"));
  if (btnSimulateFail) btnSimulateFail.addEventListener("click", () => triggerSim("workflow_run", "completed"));
}

/* GitOps Actions */
function initGitOpsActions() {
  const btnSync = document.getElementById("btn-trigger-argocd");
  const syncMsg = document.getElementById("argocd-sync-msg");

  if (!btnSync) return;
  btnSync.addEventListener("click", async () => {
    btnSync.disabled = true;
    btnSync.textContent = "Syncing with EKS...";
    try {
      const res = await fetch("/api/simulate-webhook", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          event_type: "pull_request",
          action: "closed",
          repo_name: "acme-corp/cloud-backend",
          pr_number: 104,
        }),
      });
      if (syncMsg) {
        syncMsg.textContent = "✅ ArgoCD sync triggered! Workload reconciled in Kubernetes.";
        syncMsg.style.display = "block";
      }
      incrementMetric("metric-gitops-syncs");
    } catch (e) {
      console.error(e);
    } finally {
      setTimeout(() => {
        btnSync.disabled = false;
        btnSync.textContent = "⚡ Trigger ArgoCD GitOps Sync";
      }, 2000);
    }
  });
}

/* User Authentication & GitHub Login Controller */
function initAuth() {
  const modal = document.getElementById("auth-modal");
  const btnOpenAuth = document.getElementById("btn-open-auth");
  const btnCloseModal = document.getElementById("btn-close-modal");
  const btnDemoLogin = document.getElementById("btn-demo-login");
  const tabSignin = document.getElementById("modal-tab-signin");
  const tabSignup = document.getElementById("modal-tab-signup");
  const groupUsername = document.getElementById("group-username");
  const authForm = document.getElementById("auth-form");
  const btnSubmit = document.getElementById("btn-submit-auth");
  const errorMsg = document.getElementById("auth-error-msg");
  const userProfileWidget = document.getElementById("user-profile-widget");
  const userAvatar = document.getElementById("user-avatar");
  const userName = document.getElementById("user-name");
  const btnLogout = document.getElementById("btn-logout");

  let isSignUpMode = false;

  // Check URL params for GitHub OAuth callback tokens
  const urlParams = new URLSearchParams(window.location.search);
  const callbackToken = urlParams.get("token");
  if (callbackToken) {
    localStorage.setItem("devops_auth_token", callbackToken);
    window.history.replaceState({}, document.title, window.location.pathname);
  }

  // Open & Close Modal
  if (btnOpenAuth) btnOpenAuth.addEventListener("click", () => { modal.style.display = "flex"; });
  if (btnCloseModal) btnCloseModal.addEventListener("click", () => { modal.style.display = "none"; });
  window.addEventListener("click", (e) => { if (e.target === modal) modal.style.display = "none"; });

  // Tab Toggle (Sign In vs Sign Up)
  if (tabSignin && tabSignup) {
    tabSignin.addEventListener("click", () => {
      isSignUpMode = false;
      tabSignin.style.borderBottom = "2px solid var(--accent-primary)";
      tabSignin.style.color = "var(--text-primary)";
      tabSignup.style.borderBottom = "none";
      tabSignup.style.color = "var(--text-muted)";
      groupUsername.style.display = "none";
      btnSubmit.textContent = "Sign In";
    });

    tabSignup.addEventListener("click", () => {
      isSignUpMode = true;
      tabSignup.style.borderBottom = "2px solid var(--accent-primary)";
      tabSignup.style.color = "var(--text-primary)";
      tabSignin.style.borderBottom = "none";
      tabSignin.style.color = "var(--text-muted)";
      groupUsername.style.display = "block";
      btnSubmit.textContent = "Create Account";
    });
  }

  // Instant Demo Login
  if (btnDemoLogin) {
    btnDemoLogin.addEventListener("click", async () => {
      btnDemoLogin.disabled = true;
      btnDemoLogin.textContent = "Logging in...";
      try {
        const res = await fetch("/auth/demo-login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username: "cloud-architect" }),
        });
        const data = await res.json();
        if (res.ok && data.status === "success") {
          localStorage.setItem("devops_auth_token", data.token);
          localStorage.setItem("devops_user", JSON.stringify(data.user));
          modal.style.display = "none";
          renderUserSession(data.user);
          loadRepositories();
        } else {
          errorMsg.textContent = data.detail || "Demo login failed.";
          errorMsg.style.display = "block";
        }
      } catch (err) {
        errorMsg.textContent = "Unable to reach the authentication service.";
        errorMsg.style.display = "block";
      } finally {
        btnDemoLogin.disabled = false;
        btnDemoLogin.textContent = "⚡ Instant Demo Login (Explore Repos)";
      }
    });
  }

  // Form Submit (Sign In / Sign Up)
  if (authForm) {
    authForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = document.getElementById("auth-email").value;
      const password = document.getElementById("auth-password").value;
      const username = document.getElementById("auth-username")?.value || email.split("@")[0];

      btnSubmit.disabled = true;
      errorMsg.style.display = "none";

      const endpoint = isSignUpMode ? "/auth/signup" : "/auth/login";
      const payload = isSignUpMode ? { email, password, username } : { email, password };

      try {
        const res = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (res.ok && data.status === "success") {
          localStorage.setItem("devops_auth_token", data.token);
          localStorage.setItem("devops_user", JSON.stringify(data.user));
          modal.style.display = "none";
          renderUserSession(data.user);
          loadRepositories();
        } else {
          errorMsg.textContent = data.detail || "Authentication failed.";
          errorMsg.style.display = "block";
        }
      } catch (err) {
        errorMsg.textContent = err.message;
        errorMsg.style.display = "block";
      } finally {
        btnSubmit.disabled = false;
      }
    });
  }

  // Logout
  if (btnLogout) {
    btnLogout.addEventListener("click", () => {
      localStorage.removeItem("devops_auth_token");
      localStorage.removeItem("devops_user");
      userProfileWidget.style.display = "none";
      btnOpenAuth.style.display = "inline-flex";
    });
  }

  // Check existing session
  const storedToken = localStorage.getItem("devops_auth_token");
  if (storedToken) {
    fetch("/auth/me", {
      headers: { "Authorization": `Bearer ${storedToken}` }
    })
    .then((res) => res.json())
    .then((data) => {
      if (data.authenticated && data.user) {
        renderUserSession(data.user);
      }
    })
    .catch(() => {});
  }

  function renderUserSession(user) {
    if (btnOpenAuth) btnOpenAuth.style.display = "none";
    if (userProfileWidget) {
      userProfileWidget.style.display = "flex";
      userAvatar.src = user.avatar_url || "https://avatars.githubusercontent.com/u/583231?v=4";
      userName.textContent = user.username || user.name;
    }
  }
}

/* Repositories & PR Automation Controller */
function initRepoManager() {
  const btnRefresh = document.getElementById("btn-refresh-repos");
  const searchInput = document.getElementById("repo-search-input");
  const tabReposBtn = document.getElementById("tab-btn-repos");

  if (btnRefresh) btnRefresh.addEventListener("click", loadRepositories);
  if (tabReposBtn) tabReposBtn.addEventListener("click", loadRepositories);

  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      const q = e.target.value.toLowerCase();
      const cards = document.querySelectorAll(".repo-card");
      cards.forEach((card) => {
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(q) ? "block" : "none";
      });
    });
  }
}

async function loadRepositories() {
  const container = document.getElementById("repo-list-container");
  if (!container) return;

  container.innerHTML = `<div style="color: var(--text-muted); font-size: 0.85rem; padding: 12px;">⏳ Loading connected repositories...</div>`;

  const token = localStorage.getItem("devops_auth_token");
  try {
    const res = await fetch("/auth/repos", {
      headers: token ? { "Authorization": `Bearer ${token}` } : {}
    });
    const repos = await res.json();

    container.innerHTML = repos.map((r) => `
      <div class="repo-card" onclick="selectRepository('${r.full_name}')" data-repo="${r.full_name}">
        <div class="repo-card-header">
          <span class="repo-name">📦 ${escapeHtml(r.name)}</span>
          <span class="badge ${r.devops_bot_enabled ? 'badge-success' : 'badge-primary'}" style="font-size: 0.65rem;">
            ${r.devops_bot_enabled ? 'Bot Active' : 'Setup Bot'}
          </span>
        </div>
        <div class="repo-desc">${escapeHtml(r.description)}</div>
        <div class="repo-meta">
          <span>🔵 ${escapeHtml(r.language)}</span>
          <span>⭐ ${r.stars}</span>
          <span style="color: #67e8f9;">🔀 ${r.open_prs_count} Open PRs</span>
        </div>
      </div>
    `).join("");

    // Auto-select first repo
    if (repos.length > 0) {
      selectRepository(repos[0].full_name);
    }
  } catch (err) {
    container.innerHTML = `<div style="color: var(--danger); font-size: 0.85rem;">Failed to load repositories: ${escapeHtml(err.message)}</div>`;
  }
}

async function selectRepository(repoFullName) {
  // Highlight selected card
  document.querySelectorAll(".repo-card").forEach((c) => {
    c.classList.toggle("selected", c.dataset.repo === repoFullName);
  });

  const titleEl = document.getElementById("selected-repo-title");
  const prContainer = document.getElementById("pr-list-container");
  if (titleEl) titleEl.innerHTML = `<span>📂</span> Repository: <code>${escapeHtml(repoFullName)}</code>`;

  if (!prContainer) return;
  prContainer.innerHTML = `<div style="color: var(--text-muted); font-size: 0.85rem; padding: 16px;">⏳ Fetching open Pull Requests for ${escapeHtml(repoFullName)}...</div>`;

  const token = localStorage.getItem("devops_auth_token");
  try {
    const [owner, repo] = repoFullName.split("/");
    const res = await fetch(`/auth/repos/${owner}/${repo}/pulls`, {
      headers: token ? { "Authorization": `Bearer ${token}` } : {}
    });
    const prs = await res.json();

    if (prs.length === 0) {
      prContainer.innerHTML = `<div class="output-placeholder"><span>✅</span><p>No open pull requests found for this repository.</p></div>`;
      return;
    }

    prContainer.innerHTML = prs.map((pr) => `
      <div class="pr-item-card">
        <div style="flex: 1;">
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <strong style="color: #f8fafc; font-size: 0.95rem;">#${pr.number}: ${escapeHtml(pr.title)}</strong>
            <span class="badge ${pr.risk_level === 'High' ? 'badge-danger' : pr.risk_level === 'Medium' ? 'badge-primary' : 'badge-success'}" style="font-size: 0.65rem;">
              Risk: ${escapeHtml(pr.risk_level || 'Normal')}
            </span>
          </div>
          <div style="font-size: 0.75rem; color: var(--text-muted); display: flex; gap: 12px;">
            <span>👤 Author: <code>${escapeHtml(pr.author)}</code></span>
            <span>🌿 Branch: <code>${escapeHtml(pr.branch)}</code></span>
            <span>🕒 ${escapeHtml(pr.created_at)}</span>
          </div>
        </div>

        <button class="btn btn-primary" onclick="autoReviewPR('${repoFullName}', ${pr.number}, '${escapeHtml(pr.title)}')" style="padding: 8px 14px; font-size: 0.8rem; white-space: nowrap;">
          ⚡ Auto-Review PR
        </button>
      </div>
    `).join("");
  } catch (err) {
    prContainer.innerHTML = `<div style="color: var(--danger); font-size: 0.85rem;">Failed to fetch PRs: ${escapeHtml(err.message)}</div>`;
  }
}

async function autoReviewPR(repoFullName, prNumber, prTitle) {
  // 1. Switch to PR Review Studio Tab
  const prTabBtn = document.getElementById("tab-btn-pr");
  if (prTabBtn) prTabBtn.click();

  // 2. Populate inputs
  const titleInput = document.getElementById("pr-title-input");
  const prUrlInput = document.getElementById("pr-url-input");
  const diffInput = document.getElementById("pr-diff-input");
  const fetchStatus = document.getElementById("fetch-pr-status");

  if (titleInput) titleInput.value = prTitle;
  if (prUrlInput) prUrlInput.value = `https://github.com/${repoFullName}/pull/${prNumber}`;

  if (fetchStatus) {
    fetchStatus.style.display = "block";
    fetchStatus.style.color = "#10b981";
    fetchStatus.textContent = `🚀 Loaded ${repoFullName} #${prNumber}! Running AI Code & Security Review...`;
  }

  // 3. Trigger the AI review button automatically
  const runReviewBtn = document.getElementById("btn-run-pr-review");
  if (runReviewBtn) {
    setTimeout(() => {
      runReviewBtn.click();
    }, 300);
  }
}

/* Helper Functions */
function incrementMetric(elementId) {
  const el = document.getElementById(elementId);
  if (el) {
    const val = parseInt(el.textContent, 10) || 0;
    el.textContent = val + 1;
  }
}

function escapeHtml(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/* Lightweight Markdown Formatter */
function renderMarkdown(md) {
  if (!md) return "";
  let html = md
    // Headers
    .replace(/^### (.*$)/gim, "<h3>$1</h3>")
    .replace(/^## (.*$)/gim, "<h2>$1</h2>")
    .replace(/^# (.*$)/gim, "<h1>$1</h1>")
    // Blockquotes / Alerts
    .replace(/^\> \[!WARNING\]\s*\n\> (.*$)/gim, '<blockquote style="border-left-color: #f59e0b; background: rgba(245, 158, 11, 0.1);"><strong>⚠️ WARNING:</strong> $1</blockquote>')
    .replace(/^\> \[!IMPORTANT\]\s*\n\> (.*$)/gim, '<blockquote style="border-left-color: #6366f1; background: rgba(99, 102, 241, 0.1);"><strong>ℹ️ IMPORTANT:</strong> $1</blockquote>')
    .replace(/^\> (.*$)/gim, "<blockquote>$1</blockquote>")
    // Code blocks with syntax hint
    .replace(/```suggestion\n([\s\S]*?)```/g, '<div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; border-radius: 6px; padding: 10px; margin: 10px 0;"><span style="color: #10b981; font-weight: 600; font-size: 0.8rem;">Suggested Change:</span><pre style="margin-top: 6px;"><code>$1</code></pre></div>')
    .replace(/```([a-z]*)\n([\s\S]*?)```/g, "<pre><code class=\"language-$1\">$2</code></pre>")
    // Inline code
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    // Bold / Italics
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>")
    // Tables
    .replace(/\|(.+)\|/g, (match) => {
      const cells = match.split("|").slice(1, -1);
      const isHeader = cells.some((c) => c.includes("---"));
      if (isHeader) return "";
      return "<tr>" + cells.map((c) => `<td>${c.trim()}</td>`).join("") + "</tr>";
    })
    // Unordered lists
    .replace(/^\- (.*$)/gim, "<li>$1</li>")
    // Line breaks
    .replace(/\n\n/g, "<p></p>");

  return html;
}
