# The Blind Spot — AI Critical Thinking Companion

> **PromptWars 2026 Challenge Submission**  
> *"Build a thinking companion, not a decision maker. Help users see what they may have missed, question their assumptions, recognize conflicts in their reasoning, and decide for themselves."*

---

## 1. Problem Statement

People frequently make high-stakes life, career, and engineering decisions based primarily on the information that is most visible and immediate to them (the **Anchoring Effect** and **Availability Heuristic**). In doing so, they:
- Overlook critical second-order factors and hidden costs.
- Rely on implicit, unstated, or questionable assumptions.
- Fail to recognize internal tensions and contradictions between their stated priorities and their chosen path.
- Treat immediate tangible benefits (e.g. stipend, location, excitement) as the sole evaluation criteria.

**The Challenge:** Build an AI-powered solution that helps users identify potential blind spots in their reasoning when considering a decision, without deciding for them.

---

## 2. Solution: The Blind Spot

**The Blind Spot** is an AI critical thinking companion engineered specifically to interrogate and illuminate decision reasoning. It acts as an intellectual sparring partner that mirrors the user's explicit facts, isolates cognitive anchors, identifies unstated assumptions, maps internal priority collisions, and poses neutral, non-leading questions that provoke deep reflection.

### Core Product Principle
> **BUILD A THINKING COMPANION, NOT A DECISION MAKER.**
> The system strictly adheres to neutral reflective language. It *never* declares a verdict, ranks one option as superior, or tells the user what to do. Even when adversarial users explicitly demand: *"Which should I choose?"*, the companion decomposes the reasoning and returns 100% of the agency to the user.

---

## 3. Key Features

1. **Explicit vs. Inferred Parsing**: Clearly separates what the user explicitly stated as ground truth from what can reasonably be inferred as contextual background.
2. **Cognitive Anchor Detection**: Highlights salient factors currently dominating the user's attention (e.g., immediate pay, commute time, brand prestige) and explains the specific *Anchoring Risk*.
3. **Multi-Category Blind-Spot Detection**: Surfaces unseen risks across Second-Order Effects, Opportunity Cost, Information Gaps, and Hidden Maintenance Costs.
4. **Interactive Assumption Stress-Tester**: Breaks down unstated beliefs into:
   - The assumption statement.
   - *What condition must hold for it to be true?*
   - *Risk if invalid.*
   - Interactive user stress-testing toggle (`Solid / Verified` | `High Risk` | `Needs Proof`).
5. **Conflict & Tension Radar**: Identifies direct friction between the user's stated goals and practical reality (e.g., *75% mandatory college attendance vs. 40-hour office workweeks*).
6. **Explicit Trade-Offs Matrix**: Compares what is sacrificed versus what is gained, articulating the deeper trade-off value.
7. **Missing Information Checklist**: Actionable checklist of critical data or policies the user should verify before committing, complete with interactive checkboxes.
8. **Alternative Perspectives (Mental Model Lenses)**: Views the choice from the angle of the user's 3-years-future self, an engineering mentor, and a pre-mortem failure scenario.
9. **Interactive Deep-Dive Reflection Companion**: Users can type their reflections on any generated question; the companion mirrors their thoughts, surfaces subtle biases, and probes deeper without taking sides.
10. **User's Final Decision & Synthesis Notebook**: An interactive workspace where the user formulates their personal takeaways and authors their own decision.
11. **Comprehensive Export Suite**: One-click download as a Markdown audit report (`.md`), raw structured JSON (`.json`), or clean print-friendly stylesheet.
12. **Preloaded Benchmark Scenarios**: Includes the official PromptWars internship scenario, startup vs. corporate career dilemma, legacy rewrite vs. refactor, home purchase vs. rent, and adversarial safety tests.

---

## 4. Google Services Integration

### Service Used
- **Google Gemini API** via the official Python SDK (`google-genai` >= 2.25.0)
- **Primary Model**: `gemini-3.8-flash`
- **Fallback Model**: `gemini-2.5-flash`

### Why Google Gemini Was Chosen
1. **Exceptional Nuance in Critical Reasoning**: Dissecting subtle cognitive biases, anchoring effects, and implicit assumptions requires superior linguistic comprehension and reasoning precision.
2. **Native JSON Schema Enforcement**: Gemini's structured output capability (`response_json_schema`) ensures that the 10 analysis dimensions strictly match the expected Pydantic schema without parsing errors.
3. **High Context & Efficiency**: Gemini Flash delivers near-instantaneous latency, enabling real-time deep-dive reflections while keeping inference costs minimal.
4. **Strict System Instruction Adherence**: Reliably obeys negative constraints (*"NEVER decide for the user"* and *"NEVER recommend an option"*), ensuring safety and alignment with the hackathon principles.

### Role in the Product
Google Gemini acts as the core analytical engine in `backend/gemini_service.py`:
- Categorizing explicit statements vs. contextual inferences.
- Detecting disproportionate cognitive anchoring.
- Generating domain-specific blind spots, unstated assumptions, and trade-offs.
- Powering the `/api/deep-dive` interactive reflection companion.

---

## 5. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Frontend UI                           │
│  - Semantic HTML5, ARIA Landmarks, High-Contrast CSS       │
│  - Interactive Stress-Tester & Deep Dive Reflective Drawer   │
│  - Synthesis & Decision Notebook + Markdown/JSON Exporters  │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / JSON
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (app.py)                 │
│  - /api/health          (Status & Gemini Active Flag)       │
│  - /api/scenarios       (Benchmark Scenarios Loader)        │
│  - /api/analyze         (Structured Blind Spot Analysis)    │
│  - /api/deep-dive       (Interactive Reflection Engine)     │
│  - Input Validation & Error Handlers (Pydantic Models)      │
└──────────────────────────────┬──────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
┌─────────────────────────┐           ┌─────────────────────────┐
│   Google Gemini Service │           │   Deterministic Engine  │
│    (gemini-3.8-flash)   │           │    (Heuristic Fallback) │
│ - Structured JSON Schema│           │ - Pattern Recognition   │
│ - Strict Companion Prompt│          │ - Guaranteed Offline    │
│ - High-Fidelity Insights│           │ - Full Schema Parity    │
└─────────────────────────┘           └─────────────────────────┘
```

---

## 6. Problem Statement Alignment Map

| Problem Requirement | Feature Implementation | Demonstration in The Blind Spot |
| :--- | :--- | :--- |
| **Surface Overlooked Factors** | Overlooked Factors Section | Detects academic attendance impact, mentor availability, exam crunches. |
| **Examine Assumptions** | Interactive Assumption Stress-Tester | Surfaces unstated assumptions with condition required to hold and invalidity risk. |
| **Detect Conflicts / Tensions** | Collision Radar | Highlights direct conflict between 75% attendance and 9:30-6:00 work hours. |
| **Identify Blind Spots** | Categorized Blind Spots Card Grid | Classifies blind spots into Opportunity Cost, Second-Order Effects, etc. |
| **Thoughtful Reflection Questions** | Probing Questions & Deep Dive | Generates non-leading questions (e.g. *"What if the stipend was zero?"*). |
| **Never Decide For User** | Non-Negotiable Guardrail & Synthesis | System explicitly refuses verdicts; user writes their own choice in notebook. |

---

## 7. Security Architecture

1. **Zero Hardcoded Secrets**: No API keys or credentials exist in source code.
2. **Environment Variable Configuration**: Uses `GEMINI_API_KEY` from `.env` or system environment.
3. **Optional Runtime Key**: A user-entered runtime key is supported as a developer convenience and is held only in browser `sessionStorage`; it is transmitted only in the `x-gemini-api-key` request header and is never logged or written to disk. For deployed production use, server-side `GEMINI_API_KEY` configuration is preferred.
4. **Input Sanitization**: Pydantic models validate and constrain string lengths (`max_length=4000`) and enforce minimum valid bounds.
5. **Safe Error Handling**: Custom global exception handlers prevent stack traces or internal server paths from leaking to clients.
6. **Git Protection**: `.gitignore` comprehensively ignores `.env`, cache directories, test artifacts, and logs.

---

## 8. Accessibility Considerations

- **Semantic HTML5 Elements**: Uses `<header>`, `<main>`, `<section>`, `<article>`, `<nav>`, and `<footer>`.
- **Keyboard Navigation**: Full keyboard accessibility, including a top Skip Link, visible `:focus-visible` styling rings, and shortcuts (`Ctrl+Enter` to analyze, `Esc` to dismiss modals).
- **ARIA Attributes**: `aria-live="polite"` on results workspace, `aria-expanded` on context accordions, and `aria-label` on buttons.
- **High-Contrast Palette**: The interface is designed with strong text/background contrast; formal WCAG conformance is not claimed.
- **Responsive Layout**: Fluid breakpoints optimized for Mobile (<640px), Tablet (640px-1024px), and Desktop (>1024px).

---

## 9. Comprehensive Testing

The solution includes an automated test suite executed via `pytest`.

```sh
python -m pytest tests/ -v
```

### Verified Test Suite (29 Passed Tests):
- `tests/test_analyzer.py`:
  - `test_internship_scenario_blind_spots`: Official benchmark test.
  - `test_adversarial_tell_me_what_to_choose`: Enforces that AI never decides.
  - `test_explicit_vs_inferred_separation`: Validates factual demarcation.
  - `test_deep_dive_reflection`: Tests interactive reflection mirror.
- `tests/test_api.py`:
  - `test_health_endpoint`: Verifies service status.
  - `test_list_scenarios` & `test_get_scenario_by_id`: Verifies scenario delivery.
  - `test_analyze_endpoint_valid`: Full end-to-end API analysis.
  - `test_analyze_endpoint_empty_decision`: Validates 422 error on empty input.
  - `test_analyze_endpoint_short_reasoning`: Validates 422 error on short input.
  - `test_deep_dive_endpoint_valid` & `test_deep_dive_empty_reflection`.
  - `test_serve_frontend_index`: Verifies root web application serving.
- `tests/test_edge_cases.py`:
  - `test_missing_optional_context`: Minimal inputs.
  - `test_ambiguous_decision_input`: Broad life decisions.
  - `test_long_valid_input`: Stress-testing payload boundaries.
  - `test_api_failure_fallback_resilience`: Seamless fallback to heuristic engine upon network/quota failure.
  - `test_no_decision_made_adversarial_queries`: Rejection of multiple decision-forcing prompts.
- `tests/test_models.py`:
  - Tests schema validation, boundary conditions, and required attributes.
- `tests/test_scenarios.py`:
  - Executes all 5 preloaded scenarios end-to-end.
- `tests/test_ui_responsive.py`:
  - `test_no_page_level_horizontal_overflow_css`: Strict `overflow-x: hidden` and `100vw` protection on `html` and `body`.
  - `test_grid_track_prevents_column_blowout`: Verifies `minmax(0, 1fr)` and `min-width: 0` prevent grid blowout.
  - `test_scenarios_and_filters_component_scrolling`: Verifies isolated component-level scroll on chips and tabs.
  - `test_accessible_inline_error_component_present`: Verifies accessible inline error alert replacing browser alerts.
  - `test_no_hardcoded_overwide_fixed_widths`: Verifies no unconstrained fixed widths > 360px.


---

## 10. Setup and Installation

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Google Gemini API Key (get one from [Google AI Studio](https://aistudio.google.com/))

### Quick Start

1. **Clone repository:**
   ```sh
   git clone https://github.com/SehrishCodes-ai/the_blind_spot.git
   cd the_blind_spot
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```sh
   cp .env.example .env
   # Open .env and add your GEMINI_API_KEY
   ```

4. **Run application:**
   ```sh
   python run.py
   ```

5. **Open in browser:**
   Navigate to [http://localhost:8000](http://localhost:8000).

---

## 11. Environment Variables

| Variable | Description | Default |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | Google Gemini API key for critical thinking analysis | `""` (runs heuristic fallback if absent) |
| `HOST` | Host IP address for backend server | `127.0.0.1` |
| `PORT` | Port number for backend server | `8000` |
| `GEMINI_MODEL` | Primary Gemini model identifier | `gemini-3.8-flash` |
| `GEMINI_FALLBACK_MODEL` | Fallback Gemini model identifier | `gemini-2.5-flash` |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins for deployed API access | `*` (credential-free local development) |

---

## 12. Deployment

### Container Deployment (Docker / Google Cloud Run)

A production-ready `Dockerfile` is included.

```sh
# Build docker image
docker build -t the-blind-spot .

# Run container
docker run -p 8080:8080 -e GEMINI_API_KEY="your_api_key_here" the-blind-spot
```

### Deploy to Google Cloud Run
```sh
gcloud run deploy the-blind-spot \
  --source . \
  --port 8080 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY="your_api_key_here"
```

---

## 13. PromptWars Final Criteria Compliance Audit

- [x] **CODE QUALITY**: Modular separation of concerns (`backend/`, `frontend/`, `tests/`), clean Pydantic typing, zero dead code, focused functions.
- [x] **SECURITY**: Zero hardcoded credentials, server-side input validation, configurable credential-free CORS, `.env` git-ignored, no stack trace exposure.
- [x] **EFFICIENCY**: Single targeted inference call per analysis, client-side session caching, minimal dependency footprint.
- [x] **TESTING**: 29 automated tests covering standard inputs, edge cases, API outages, schema boundaries, responsive UI, and adversarial attempts.
- [x] **ACCESSIBILITY**: Semantic HTML5, keyboard shortcuts, visible focus indicators, screen-reader landmarks, responsive across mobile/tablet/desktop.
- [x] **PROBLEM STATEMENT ALIGNMENT**: Direct implementation of the thinking companion principle; official internship benchmark fully solved.
- [x] **GOOGLE SERVICES USAGE**: Meaningful, deep integration with Google Gemini (`gemini-3.8-flash`) via the modern `google-genai` SDK with structured schema generation.
