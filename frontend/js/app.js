/**
 * The Blind Spot — Application Logic
 * AI Critical Thinking Companion
 */

let currentAnalysis = null;
let activeScenarioId = null;

// Loading step messages
const LOADING_STEPS = [
  "Reading your decision and reasoning context...",
  "Distinguishing explicitly stated facts from inferences...",
  "Identifying cognitive anchors & prominent visible factors...",
  "Searching for potential blind spots & unexamined angles...",
  "Interrogating unstated assumptions & preconditions...",
  "Detecting internal conflicts, contradictions & trade-offs...",
  "Formulating neutral, non-leading reflective questions..."
];

// Document Ready Initialization
document.addEventListener("DOMContentLoaded", () => {
  initScenarios();
  setupEventListeners();
  checkBackendHealth();
  loadSavedApiKey();
});

/**
 * Initialize Scenario Switcher
 */
function initScenarios() {
  const container = document.getElementById("scenariosContainer");
  if (!container || typeof SCENARIOS_DATA === "undefined") return;

  container.innerHTML = "";
  SCENARIOS_DATA.forEach((sc) => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "scenario-chip";
    chip.id = `chip-${sc.id}`;
    chip.setAttribute("aria-label", `Load scenario: ${sc.title}`);
    chip.innerHTML = `
      <div class="scenario-chip-title">
        <span>${sc.shortTitle}</span>
        ${sc.badge ? `<span class="badge-official">${sc.badge}</span>` : ""}
      </div>
      <div class="scenario-chip-subtitle">${sc.subtitle}</div>
    `;
    chip.addEventListener("click", () => loadScenario(sc.id));
    container.appendChild(chip);
  });
}

/**
 * Load a specific scenario into the input form
 */
function loadScenario(scenarioId) {
  const sc = SCENARIOS_DATA.find((s) => s.id === scenarioId);
  if (!sc) return;

  activeScenarioId = scenarioId;

  // Clear any existing error
  clearInlineError();

  // Update active chip UI
  document.querySelectorAll(".scenario-chip").forEach((c) => c.classList.remove("active"));
  const activeChip = document.getElementById(`chip-${scenarioId}`);
  if (activeChip) activeChip.classList.add("active");

  // Populate fields
  document.getElementById("decisionInput").value = sc.decision;
  document.getElementById("reasoningInput").value = sc.reasoning;
  document.getElementById("prioritiesInput").value = sc.priorities || "";
  document.getElementById("constraintsInput").value = sc.constraints || "";
  document.getElementById("optionsInput").value = (sc.options_considered || []).join("\n");

  // If optional fields are filled, expand accordion
  const accordion = document.getElementById("advancedContext");
  if (accordion && !accordion.classList.contains("open")) {
    toggleAccordion();
  }

  // Focus and scroll to form smoothly
  const form = document.getElementById("decisionForm");
  if (form) {
    form.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
}

/**
 * Event Listeners Setup
 */
function setupEventListeners() {
  // Form submission
  const form = document.getElementById("decisionForm");
  if (form) {
    form.addEventListener("submit", handleAnalyzeSubmit);
  }

  // Keyboard shortcut Ctrl+Enter or Cmd+Enter
  window.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      const activeEl = document.activeElement;
      if (activeEl && (activeEl.tagName === "TEXTAREA" || activeEl.tagName === "INPUT")) {
        e.preventDefault();
        handleAnalyzeSubmit(e);
      }
    }
    if (e.key === "Escape") {
      closeAllModals();
    }
  });

  // Real-time input error dismissal
  const decisionInput = document.getElementById("decisionInput");
  if (decisionInput) {
    decisionInput.addEventListener("input", () => {
      decisionInput.classList.remove("is-invalid");
      clearInlineError();
    });
  }

  const reasoningInput = document.getElementById("reasoningInput");
  if (reasoningInput) {
    reasoningInput.addEventListener("input", () => {
      reasoningInput.classList.remove("is-invalid");
      clearInlineError();
    });
  }

  // Inline error close button
  const errorCloseBtn = document.getElementById("inlineErrorClose");
  if (errorCloseBtn) {
    errorCloseBtn.addEventListener("click", clearInlineError);
  }

  // Accordion Toggle
  const toggleBtn = document.getElementById("accordionToggle");
  if (toggleBtn) {
    toggleBtn.addEventListener("click", toggleAccordion);
  }

  // Clear Form
  const clearBtn = document.getElementById("clearBtn");
  if (clearBtn) {
    clearBtn.addEventListener("click", handleClearForm);
  }

  // Settings Modal
  const settingsBtn = document.getElementById("settingsBtn");
  if (settingsBtn) {
    settingsBtn.addEventListener("click", openSettingsModal);
  }
  const closeSettingsBtn = document.getElementById("closeSettingsBtn");
  if (closeSettingsBtn) {
    closeSettingsBtn.addEventListener("click", closeAllModals);
  }
  const saveSettingsBtn = document.getElementById("saveSettingsBtn");
  if (saveSettingsBtn) {
    saveSettingsBtn.addEventListener("click", saveSettings);
  }

  // Export Buttons
  const exportMdBtn = document.getElementById("exportMdBtn");
  if (exportMdBtn) {
    exportMdBtn.addEventListener("click", exportMarkdown);
  }
  const exportJsonBtn = document.getElementById("exportJsonBtn");
  if (exportJsonBtn) {
    exportJsonBtn.addEventListener("click", exportJson);
  }
  const printBtn = document.getElementById("printBtn");
  if (printBtn) {
    printBtn.addEventListener("click", () => window.print());
  }

  // Filters
  document.querySelectorAll(".filter-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      document.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
      e.target.classList.add("active");
      applyFilter(e.target.dataset.filter);
    });
  });
}

/**
 * Inline Error Handling (Accessible & integrated replacement for browser alerts)
 */
function showInlineError(title, message, targetInputId) {
  const alertEl = document.getElementById("inlineErrorAlert");
  const titleEl = document.getElementById("inlineErrorTitle");
  const msgEl = document.getElementById("inlineErrorMessage");

  if (titleEl) titleEl.textContent = title;
  if (msgEl) msgEl.textContent = message;
  if (alertEl) {
    alertEl.classList.add("open");
    alertEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  if (targetInputId) {
    const inputEl = document.getElementById(targetInputId);
    if (inputEl) {
      inputEl.classList.add("is-invalid");
      inputEl.focus();
    }
  }
}

function clearInlineError() {
  const alertEl = document.getElementById("inlineErrorAlert");
  if (alertEl) {
    alertEl.classList.remove("open");
  }
  document.querySelectorAll(".form-control.is-invalid").forEach((el) => {
    el.classList.remove("is-invalid");
  });
}

function toggleAccordion() {
  const content = document.getElementById("advancedContext");
  const toggleBtn = document.getElementById("accordionToggle");
  if (!content) return;
  const isOpen = content.classList.contains("open");
  if (isOpen) {
    content.classList.remove("open");
    toggleBtn.setAttribute("aria-expanded", "false");
    toggleBtn.innerHTML = `<span>+ Add priorities, constraints & options</span>`;
  } else {
    content.classList.add("open");
    toggleBtn.setAttribute("aria-expanded", "true");
    toggleBtn.innerHTML = `<span>− Hide additional context</span>`;
  }
}

function handleClearForm() {
  clearInlineError();
  document.getElementById("decisionInput").value = "";
  document.getElementById("reasoningInput").value = "";
  document.getElementById("prioritiesInput").value = "";
  document.getElementById("constraintsInput").value = "";
  document.getElementById("optionsInput").value = "";
  document.querySelectorAll(".scenario-chip").forEach((c) => c.classList.remove("active"));
  activeScenarioId = null;
  document.getElementById("decisionInput").focus();
}

/**
 * Submit and Analyze
 */
async function handleAnalyzeSubmit(e) {
  if (e) e.preventDefault();
  clearInlineError();

  const decision = document.getElementById("decisionInput").value.trim();
  const reasoning = document.getElementById("reasoningInput").value.trim();
  const priorities = document.getElementById("prioritiesInput").value.trim();
  const constraints = document.getElementById("constraintsInput").value.trim();
  const optionsRaw = document.getElementById("optionsInput").value.trim();
  const optionsConsidered = optionsRaw ? optionsRaw.split("\n").map((o) => o.trim()).filter(Boolean) : [];

  if (!decision || decision.length < 3) {
    showInlineError(
      "Let's add a little more context",
      "Please enter the decision or situation you are considering (at least 3 characters).",
      "decisionInput"
    );
    return;
  }
  // Must contain at least one letter (any Unicode script: Latin, Devanagari, Arabic, etc.)
  // This rejects "123456", "!!! ???" while keeping "₹15,000 stipend" or "6-month internship"
  if (!/\p{L}/u.test(decision)) {
    showInlineError(
      "Please describe your decision in words",
      "Numbers or symbols alone can't be analyzed. Try something like \"Should I accept this internship?\"",
      "decisionInput"
    );
    return;
  }
  if (!reasoning || reasoning.length < 10) {
    showInlineError(
      "Help us understand your current perspective",
      "Please provide at least 10 characters explaining your current reasoning and visible factors.",
      "reasoningInput"
    );
    return;
  }
  // Reasoning must also contain at least one letter
  if (!/\p{L}/u.test(reasoning)) {
    showInlineError(
      "Please explain your reasoning in words",
      "Numbers or symbols alone can't be analyzed. Describe the factors influencing your thinking.",
      "reasoningInput"
    );
    return;
  }

  // Show loading state
  showLoading(true);

  const payload = {
    decision,
    reasoning,
    priorities,
    constraints,
    options_considered: optionsConsidered
  };

  const headers = { "Content-Type": "application/json" };
  const customKey = sessionStorage.getItem("gemini_api_key");
  if (customKey) {
    headers["x-gemini-api-key"] = customKey;
  }

  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers,
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.message || err.detail || "Analysis request failed.");
    }

    const data = await res.json();
    currentAnalysis = data;
    renderAnalysis(data);
  } catch (error) {
    console.error("Analysis Error:", error);
    showInlineError(
      "Analysis Temporarily Unavailable",
      "We encountered an issue analyzing your reasoning: " + (error.message || "Please try again."),
      null
    );
  } finally {
    showLoading(false);
  }
}

/**
 * Loading Animation Controller
 */
let loadingInterval = null;
function showLoading(isLoading) {
  const emptyState = document.getElementById("emptyState");
  const loadingState = document.getElementById("loadingState");
  const resultsContent = document.getElementById("resultsContent");
  const analyzeBtn = document.getElementById("analyzeBtn");

  if (isLoading) {
    emptyState.style.display = "none";
    resultsContent.style.display = "none";
    loadingState.style.display = "block";
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = `<span>Analyzing...</span>`;

    let stepIdx = 0;
    const stepTextEl = document.getElementById("loadingStepText");
    if (stepTextEl) {
      stepTextEl.textContent = LOADING_STEPS[0];
      clearInterval(loadingInterval);
      loadingInterval = setInterval(() => {
        stepIdx = (stepIdx + 1) % LOADING_STEPS.length;
        stepTextEl.textContent = LOADING_STEPS[stepIdx];
      }, 1400);
    }
  } else {
    clearInterval(loadingInterval);
    loadingState.style.display = "none";
    analyzeBtn.disabled = false;
    analyzeBtn.innerHTML = `<span>Analyze My Reasoning</span>`;
  }
}

/**
 * Render Complete Structured Analysis
 * Only displays sections that have meaningful content.
 */
function renderAnalysis(data) {
  document.getElementById("emptyState").style.display = "none";
  const resultsContent = document.getElementById("resultsContent");
  resultsContent.style.display = "flex";

  // Summary badge
  document.getElementById("resultDecisionTitle").textContent = data.decision_summary;
  document.getElementById("resultEngineBadge").textContent = `${data.model_provider} (${data.model_name})`;

  // Render 1. Understanding (Only if available)
  renderSection("sec-understanding", data.understanding, renderUnderstanding);

  // Render 2. Most Visible Factors (Anchoring)
  renderSection("sec-visible", data.most_visible_factors, renderVisibleFactors);

  // Render 3. Potential Blind Spots
  renderSection("sec-blindspots", data.potential_blind_spots, renderBlindSpots);

  // Render 4. Assumptions to Examine
  renderSection("sec-assumptions", data.assumptions_to_examine, renderAssumptions);

  // Render 5. Overlooked Factors
  renderSection("sec-overlooked", data.overlooked_factors, renderOverlooked);

  // Render 6. Conflicts & Tensions
  renderSection("sec-conflicts", data.conflicts_and_tensions, renderConflicts);

  // Render 7. Trade-offs
  renderSection("sec-tradeoffs", data.trade_offs, renderTradeOffs);

  // Render 8. Missing Information
  renderSection("sec-missing", data.missing_information, renderMissingInfo);

  // Render 9. Alternative Perspectives
  renderSection("sec-perspectives", data.alternative_perspectives, renderPerspectives);

  // Render 10. Reflective Questions
  renderSection("sec-questions", data.reflective_questions, renderQuestions);

  // Render Reminder
  document.getElementById("ownershipStatement").textContent = data.decision_ownership_statement;

  // Scroll smoothly to results
  resultsContent.scrollIntoView({ behavior: "smooth", block: "start" });
}

/**
 * Helper to render section conditionally without forcing irrelevant categories
 */
function renderSection(sectionElementId, items, renderFn) {
  const el = document.getElementById(sectionElementId);
  if (!el) return;
  if (!items || items.length === 0) {
    el.style.display = "none";
  } else {
    el.style.display = "block";
    renderFn(items);
  }
}

function renderUnderstanding(items) {
  const container = document.getElementById("understandingList");
  container.innerHTML = "";

  items.forEach((u) => {
    const card = document.createElement("div");
    card.className = "insight-card";
    const badgeClass = u.fact_type === "explicit" ? "badge-explicit" : "badge-inferred";
    const badgeText = u.fact_type === "explicit" ? "Explicit Fact" : "Contextual Inference";

    card.innerHTML = `
      <div class="card-top">
        <span class="badge ${badgeClass}">${badgeText}</span>
      </div>
      <div class="card-title">${escapeHtml(u.content)}</div>
      ${u.source_context ? `<div class="card-body-text" style="font-size:0.8rem; color:var(--text-muted);">${escapeHtml(u.source_context)}</div>` : ""}
    `;
    container.appendChild(card);
  });
}

function renderVisibleFactors(items) {
  const container = document.getElementById("visibleFactorsList");
  container.innerHTML = "";

  items.forEach((v) => {
    const card = document.createElement("div");
    card.className = "insight-card";
    card.innerHTML = `
      <div class="card-top">
        <div class="card-title">👁️ ${escapeHtml(v.factor)}</div>
        <span class="badge badge-moderate">Prominent Anchor</span>
      </div>
      <div class="card-body-text"><strong>Why Prominent:</strong> ${escapeHtml(v.why_prominent)}</div>
      <div class="card-condition-box">
        <strong>Anchoring Risk</strong>
        ${escapeHtml(v.anchoring_risk)}
      </div>
    `;
    container.appendChild(card);
  });
}

function renderBlindSpots(items) {
  const container = document.getElementById("blindSpotsList");
  container.innerHTML = "";

  items.forEach((b) => {
    const card = document.createElement("div");
    card.className = "insight-card";
    const severityBadge = b.severity === "critical" ? "badge-critical" : "badge-significant";
    card.innerHTML = `
      <div class="card-top">
        <div class="card-title">🕶️ ${escapeHtml(b.title)}</div>
        <span class="badge ${severityBadge}">${escapeHtml(b.category || b.severity)}</span>
      </div>
      <div class="card-body-text">${escapeHtml(b.description)}</div>
    `;
    container.appendChild(card);
  });
}

function renderAssumptions(items) {
  const container = document.getElementById("assumptionsList");
  container.innerHTML = "";

  items.forEach((a, idx) => {
    const card = document.createElement("div");
    card.className = "insight-card";
    card.id = `assumption-card-${idx}`;
    card.innerHTML = `
      <div class="card-top">
        <div class="card-title">🧩 Assumption #${idx + 1}</div>
        <span class="badge badge-inferred">Unstated Premise</span>
      </div>
      <div class="card-body-text">"${escapeHtml(a.assumption)}"</div>
      <div class="card-condition-box">
        <strong>Condition Required to Hold</strong>
        ${escapeHtml(a.condition_to_hold)}
      </div>
      <div class="card-body-text" style="color:var(--color-danger); font-size:0.825rem;">
        <strong>Risk if Invalid:</strong> ${escapeHtml(a.risk_if_invalid)}
      </div>
      <div class="assumption-controls">
        <span style="font-size:0.75rem; color:var(--text-muted); margin-right:0.3rem;">Your Assessment:</span>
        <button type="button" class="stress-btn solid" onclick="setAssumptionState(${idx}, 'solid')">✓ Solid / Verified</button>
        <button type="button" class="stress-btn risk" onclick="setAssumptionState(${idx}, 'risk')">⚠ High Risk</button>
        <button type="button" class="stress-btn unverified" onclick="setAssumptionState(${idx}, 'unverified')">? Needs Proof</button>
      </div>
    `;
    container.appendChild(card);
  });
}

window.setAssumptionState = function(idx, state) {
  const card = document.getElementById(`assumption-card-${idx}`);
  if (!card) return;
  card.querySelectorAll(".stress-btn").forEach((b) => b.classList.remove("active"));
  const btn = card.querySelector(`.stress-btn.${state}`);
  if (btn) btn.classList.add("active");
};

function renderOverlooked(items) {
  const container = document.getElementById("overlookedList");
  container.innerHTML = "";

  items.forEach((o) => {
    const card = document.createElement("div");
    card.className = "insight-card";
    card.innerHTML = `
      <div class="card-top">
        <div class="card-title">${escapeHtml(o.factor)}</div>
        <span class="badge badge-moderate">${escapeHtml(o.dimension)}</span>
      </div>
      <div class="card-body-text"><strong>Potential Impact:</strong> ${escapeHtml(o.potential_impact)}</div>
    `;
    container.appendChild(card);
  });
}

function renderConflicts(items) {
  const container = document.getElementById("conflictsList");
  container.innerHTML = "";

  items.forEach((c) => {
    const card = document.createElement("div");
    card.className = "insight-card tension-card";
    const elemA = c.conflicting_elements[0] || "Priority A";
    const elemB = c.conflicting_elements[1] || "Commitment B";

    card.innerHTML = `
      <div class="card-top">
        <div class="card-title">⚡ ${escapeHtml(c.title)}</div>
        <span class="badge badge-significant">Tension</span>
      </div>
      <div class="tension-collision">
        <div class="tension-item">${escapeHtml(elemA)}</div>
        <div class="tension-vs">VS</div>
        <div class="tension-item">${escapeHtml(elemB)}</div>
      </div>
      <div class="card-body-text">${escapeHtml(c.explanation)}</div>
    `;
    container.appendChild(card);
  });
}

function renderTradeOffs(items) {
  const container = document.getElementById("tradeOffsList");
  container.innerHTML = "";

  items.forEach((t) => {
    const card = document.createElement("div");
    card.className = "insight-card";
    card.innerHTML = `
      <div class="tradeoff-row">
        <div class="tradeoff-box tradeoff-sacrifice">
          <strong style="display:block; font-size:0.72rem; text-transform:uppercase; margin-bottom:0.25rem;">Giving Up</strong>
          ${escapeHtml(t.giving_up)}
        </div>
        <div class="tradeoff-box tradeoff-gain">
          <strong style="display:block; font-size:0.72rem; text-transform:uppercase; margin-bottom:0.25rem;">Gaining</strong>
          ${escapeHtml(t.gaining)}
        </div>
      </div>
      <div class="card-body-text" style="font-size:0.825rem; color:var(--text-muted); margin-top:0.25rem;">
        <strong>Underlying Core Value:</strong> ${escapeHtml(t.underlying_value)}
      </div>
    `;
    container.appendChild(card);
  });
}

function renderMissingInfo(items) {
  const container = document.getElementById("missingInfoList");
  container.innerHTML = "";

  items.forEach((m, idx) => {
    const card = document.createElement("div");
    card.className = "insight-card";
    card.innerHTML = `
      <div class="card-top">
        <label style="display:flex; align-items:center; gap:0.6rem; cursor:pointer; flex:1;">
          <input type="checkbox" id="check-info-${idx}" style="accent-color:var(--accent-cyan); width:18px; height:18px; flex-shrink:0;">
          <span class="card-title" style="font-size:0.92rem;">${escapeHtml(m.item_needed)}</span>
        </label>
        <span class="badge badge-inferred">Verification Needed</span>
      </div>
      <div class="card-body-text"><strong>Why Critical:</strong> ${escapeHtml(m.why_critical)}</div>
      <div class="card-condition-box">
        <strong>Suggested Action to Verify</strong>
        ${escapeHtml(m.how_to_verify)}
      </div>
    `;
    container.appendChild(card);
  });
}

function renderPerspectives(items) {
  const container = document.getElementById("perspectivesList");
  container.innerHTML = "";

  items.forEach((p) => {
    const card = document.createElement("div");
    card.className = "insight-card";
    card.innerHTML = `
      <div class="card-top">
        <div class="card-title">🔮 ${escapeHtml(p.angle_name)}</div>
      </div>
      <div class="card-body-text">${escapeHtml(p.perspective_description)}</div>
    `;
    container.appendChild(card);
  });
}

function renderQuestions(items) {
  const container = document.getElementById("questionsList");
  container.innerHTML = "";

  items.forEach((q, idx) => {
    const card = document.createElement("div");
    card.className = "insight-card question-card";
    card.id = `q-card-${idx}`;
    card.innerHTML = `
      <div class="card-top">
        <div class="card-title">❓ ${escapeHtml(q.question)}</div>
        <span class="badge" style="background:rgba(192,132,252,0.15); color:var(--accent-purple);">Reflective Focus</span>
      </div>
      <div class="card-body-text" style="font-size:0.825rem; color:var(--text-muted);">
        <strong>Purpose:</strong> ${escapeHtml(q.purpose)} (${escapeHtml(q.suggested_focus)})
      </div>
      <div class="reflect-action-bar">
        <button type="button" class="btn btn-outline btn-sm" onclick="toggleReflectionDrawer(${idx})">
          💬 Reflect On This
        </button>
      </div>
      <div class="reflection-drawer" id="reflection-drawer-${idx}">
        <label for="reflection-input-${idx}" style="font-size:0.825rem; font-weight:600; display:block; margin-bottom:0.4rem;">
          Your honest thoughts on this question:
        </label>
        <textarea class="form-control" id="reflection-input-${idx}" rows="3" placeholder="Type what comes to mind when you honestly examine this question..."></textarea>
        <div id="reflection-error-${idx}" style="display:none; color:#fca5a5; font-size:0.75rem; margin-top:0.4rem;">Please enter your reflection first.</div>
        <div style="display:flex; justify-content:flex-end; gap:0.5rem; margin-top:0.75rem;">
          <button type="button" class="btn btn-primary btn-sm" id="reflect-submit-btn-${idx}" onclick="submitDeepDive(${idx}, '${escapeQuotes(q.question)}')">
            Explore With Thinking Companion
          </button>
        </div>
        <div class="deep-dive-results" id="deep-dive-results-${idx}" style="display:none;"></div>
      </div>
    `;
    container.appendChild(card);
  });
}

window.toggleReflectionDrawer = function(idx) {
  const drawer = document.getElementById(`reflection-drawer-${idx}`);
  if (!drawer) return;
  drawer.classList.toggle("open");
};

window.submitDeepDive = async function(idx, questionText) {
  const inputEl = document.getElementById(`reflection-input-${idx}`);
  const resultsEl = document.getElementById(`deep-dive-results-${idx}`);
  const errEl = document.getElementById(`reflection-error-${idx}`);
  const btn = document.getElementById(`reflect-submit-btn-${idx}`);

  if (errEl) errEl.style.display = "none";
  const userReflection = inputEl.value.trim();
  if (!userReflection) {
    if (errEl) {
      errEl.style.display = "block";
    }
    inputEl.focus();
    return;
  }

  btn.disabled = true;
  btn.textContent = "Reflecting...";

  const headers = { "Content-Type": "application/json" };
  const customKey = sessionStorage.getItem("gemini_api_key");
  if (customKey) headers["x-gemini-api-key"] = customKey;

  try {
    const res = await fetch("/api/deep-dive", {
      method: "POST",
      headers,
      body: JSON.stringify({
        decision: currentAnalysis ? currentAnalysis.decision_summary : "My Decision",
        selected_question_or_assumption: questionText,
        user_reflection: userReflection
      })
    });

    if (!res.ok) throw new Error("Deep dive reflection failed.");
    const data = await res.json();

    resultsEl.style.display = "block";
    resultsEl.innerHTML = `
      <h5>Companion's Neutral Mirror</h5>
      <p style="margin-bottom:0.6rem; line-height:1.55;">${escapeHtml(data.reflective_mirror)}</p>
      <h5 style="margin-top:0.75rem;">Probing Questions to Ponder</h5>
      <ul style="padding-left:1.25rem; line-height:1.6;">
        ${data.probing_follow_up_questions.map((q) => `<li>${escapeHtml(q)}</li>`).join("")}
      </ul>
      <div style="font-size:0.75rem; color:var(--text-muted); margin-top:0.75rem; font-style:italic;">
        ${escapeHtml(data.reminder)}
      </div>
    `;
  } catch (err) {
    console.error(err);
    if (errEl) {
      errEl.textContent = "Could not load reflection: " + err.message;
      errEl.style.display = "block";
    }
  } finally {
    btn.disabled = false;
    btn.textContent = "Explore With Thinking Companion";
  }
};

/**
 * Filter sections
 */
function applyFilter(filter) {
  const sections = {
    all: ["sec-understanding", "sec-visible", "sec-blindspots", "sec-assumptions", "sec-overlooked", "sec-conflicts", "sec-tradeoffs", "sec-missing", "sec-perspectives", "sec-questions"],
    visible: ["sec-visible", "sec-understanding"],
    blindspots: ["sec-blindspots", "sec-overlooked"],
    assumptions: ["sec-assumptions"],
    tensions: ["sec-conflicts", "sec-tradeoffs"],
    questions: ["sec-questions", "sec-perspectives"]
  };

  const toShow = sections[filter] || sections.all;
  sections.all.forEach((secId) => {
    const el = document.getElementById(secId);
    if (el) {
      // Only display if both in the filter AND contains child cards
      const hasCards = el.querySelectorAll(".insight-card").length > 0;
      el.style.display = toShow.includes(secId) && hasCards ? "block" : "none";
    }
  });
}

/**
 * Export to Markdown
 */
function exportMarkdown() {
  if (!currentAnalysis) return;
  const userSynthesis = document.getElementById("userSynthesisNotes") ? document.getElementById("userSynthesisNotes").value : "";
  const userDecision = document.getElementById("userDecisionText") ? document.getElementById("userDecisionText").value : "";

  let md = `# The Blind Spot — Critical Thinking & Decision Audit Report\n\n`;
  md += `**Decision Under Consideration:** ${currentAnalysis.decision_summary}\n`;
  md += `**Date of Analysis:** ${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()}\n`;
  md += `**Engine:** ${currentAnalysis.model_provider} (${currentAnalysis.model_name})\n\n`;
  md += `> *Note: This analysis was generated as a thinking companion. The final judgment and decision remain completely with the user.*\n\n`;

  if (currentAnalysis.understanding && currentAnalysis.understanding.length > 0) {
    md += `## 1. What Was Understood\n`;
    currentAnalysis.understanding.forEach((u) => {
      md += `- [${u.fact_type.toUpperCase()}] ${u.content}\n`;
    });
    md += `\n`;
  }

  if (currentAnalysis.most_visible_factors && currentAnalysis.most_visible_factors.length > 0) {
    md += `## 2. Most Prominent Visible Factors (Cognitive Anchors)\n`;
    currentAnalysis.most_visible_factors.forEach((v) => {
      md += `### ${v.factor}\n- **Why Visible:** ${v.why_prominent}\n- **Anchoring Risk:** ${v.anchoring_risk}\n\n`;
    });
  }

  if (currentAnalysis.potential_blind_spots && currentAnalysis.potential_blind_spots.length > 0) {
    md += `## 3. Potential Blind Spots\n`;
    currentAnalysis.potential_blind_spots.forEach((b) => {
      md += `### [${b.category}] ${b.title}\n${b.description}\n\n`;
    });
  }

  if (currentAnalysis.assumptions_to_examine && currentAnalysis.assumptions_to_examine.length > 0) {
    md += `## 4. Assumptions to Interrogate\n`;
    currentAnalysis.assumptions_to_examine.forEach((a, i) => {
      md += `### Assumption ${i + 1}: "${a.assumption}"\n- **Condition Needed to Hold:** ${a.condition_to_hold}\n- **Risk if Invalid:** ${a.risk_if_invalid}\n\n`;
    });
  }

  if (currentAnalysis.overlooked_factors && currentAnalysis.overlooked_factors.length > 0) {
    md += `## 5. Overlooked Factors\n`;
    currentAnalysis.overlooked_factors.forEach((o) => {
      md += `- **${o.factor}** (${o.dimension}): ${o.potential_impact}\n`;
    });
    md += `\n`;
  }

  if (currentAnalysis.conflicts_and_tensions && currentAnalysis.conflicts_and_tensions.length > 0) {
    md += `## 6. Conflicts & Reasoning Tensions\n`;
    currentAnalysis.conflicts_and_tensions.forEach((c) => {
      md += `### ${c.title}\n- **Collision:** ${c.conflicting_elements.join(" vs ")}\n- **Explanation:** ${c.explanation}\n\n`;
    });
  }

  if (currentAnalysis.trade_offs && currentAnalysis.trade_offs.length > 0) {
    md += `## 7. Explicit Trade-Offs\n`;
    currentAnalysis.trade_offs.forEach((t) => {
      md += `- Giving Up: ${t.giving_up} ↔ Gaining: ${t.gaining} (Core Value: ${t.underlying_value})\n`;
    });
    md += `\n`;
  }

  if (currentAnalysis.missing_information && currentAnalysis.missing_information.length > 0) {
    md += `## 8. Missing Information to Verify\n`;
    currentAnalysis.missing_information.forEach((m) => {
      md += `- **${m.item_needed}:** ${m.why_critical} *(Verify via: ${m.how_to_verify})*\n`;
    });
    md += `\n`;
  }

  if (currentAnalysis.reflective_questions && currentAnalysis.reflective_questions.length > 0) {
    md += `## 9. Reflective Questions\n`;
    currentAnalysis.reflective_questions.forEach((q) => {
      md += `- **${q.question}** (Purpose: ${q.purpose})\n`;
    });
    md += `\n`;
  }

  if (userSynthesis || userDecision) {
    md += `## 10. User's Personal Synthesis & Final Decision\n`;
    if (userSynthesis) md += `### Personal Takeaways & Reflection Notes\n${userSynthesis}\n\n`;
    if (userDecision) md += `### User's Final Chosen Path\n${userDecision}\n\n`;
  }

  downloadFile("The_Blind_Spot_Decision_Audit.md", md, "text/markdown");
}

/**
 * Export to JSON
 */
function exportJson() {
  if (!currentAnalysis) return;
  const userSynthesis = document.getElementById("userSynthesisNotes") ? document.getElementById("userSynthesisNotes").value : "";
  const userDecision = document.getElementById("userDecisionText") ? document.getElementById("userDecisionText").value : "";

  const exportPayload = {
    ...currentAnalysis,
    exported_at: new Date().toISOString(),
    user_synthesis: userSynthesis,
    user_final_decision: userDecision
  };

  downloadFile("The_Blind_Spot_Analysis.json", JSON.stringify(exportPayload, null, 2), "application/json");
}

function downloadFile(filename, content, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Check Backend Health
 */
async function checkBackendHealth() {
  const badge = document.getElementById("backendStatusBadge");
  try {
    const res = await fetch("/api/health");
    if (res.ok) {
      const data = await res.json();
      if (badge) {
        if (data.gemini_api_configured) {
          badge.innerHTML = `🟢 Google Gemini Active (${data.default_model})`;
          badge.style.color = "var(--color-success)";
        } else {
          badge.innerHTML = `🟡 Deterministic Reasoning Engine (Ready)`;
          badge.style.color = "var(--color-warning)";
        }
      }
    }
  } catch (err) {
    if (badge) {
      badge.innerHTML = `🔴 Server Disconnected`;
      badge.style.color = "var(--color-danger)";
    }
  }
}

/**
 * Settings Modal Logic
 */
function openSettingsModal() {
  const modal = document.getElementById("settingsModal");
  if (modal) modal.classList.add("open");
}

function closeAllModals() {
  document.querySelectorAll(".modal-overlay").forEach((m) => m.classList.remove("open"));
}

function saveSettings() {
  const keyInput = document.getElementById("modalGeminiKeyInput");
  if (keyInput) {
    const key = keyInput.value.trim();
    if (key) {
      sessionStorage.setItem("gemini_api_key", key);
    } else {
      sessionStorage.removeItem("gemini_api_key");
    }
  }
  closeAllModals();
  checkBackendHealth();
}

function loadSavedApiKey() {
  const saved = sessionStorage.getItem("gemini_api_key");
  const input = document.getElementById("modalGeminiKeyInput");
  if (saved && input) {
    input.value = saved;
  }
}

/**
 * HTML Escaping Helpers
 */
function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function escapeQuotes(str) {
  if (!str) return "";
  return String(str).replace(/'/g, "\\'").replace(/"/g, "&quot;");
}
