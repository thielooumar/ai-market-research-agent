# High‑Level Design Document

## 1. Overview
The **B2B Interview Strategist** solution consists of two main components:
1. **Agent (backend logic)** – Python code that implements Gemini‑powered market research, target‑company discovery, email/guide generation, and contact lookup.
2. **Web UI** – A single‑page JavaScript/HTML application that lets users create sections, run market‑research, and interact with the agent via REST endpoints.

Both components run on **Google Cloud Run** (managed service) and communicate over HTTP. The UI is served as static files by FastAPI; the agent functions are exposed as `/api/*` endpoints.

---
## 2. Directory Structure (as of the current repository)
```
build-with-gemini/          # Workspace root (git repo)
│
├─ frontend/               # UI layer
│   ├─ static/             # Static assets served by FastAPI
│   │   ├─ index.html      # Main page (HTML + embedded JS/CSS)
│   │   ├─ style.css       # Global styles (Tailwind‑like custom CSS)
│   │   └─ ...
│   └─ main.py             # FastAPI entry‑point, static‑file mount & API routes
│
├─ app/                    # Agent / business‑logic layer
│   ├─ __init__.py
│   ├─ tools.py            # Core functions (market research, target discovery, …)
│   └─ ...
│
├─ Dockerfile              # Multi‑stage build – copies `frontend` and `app`
├─ entrypoint.sh           # Starts `uvicorn` server
└─ requirements.txt        # Python dependencies (FastAPI, google‑genai, …)
```

- **`frontend/main.py`** creates a FastAPI app, mounts the static directory, and defines the API endpoints (`/api/market-research`, `/api/analyze`, `/api/contact`, etc.).
- **`app/tools.py`** contains the heavy lifting: calls to Gemini (via `google‑genai`), data processing, and fallback static matrices.
- **`Dockerfile`** builds the container, installs dependencies, and sets the entrypoint.

---
## 3. Agent (Backend) Details
| Module | Responsibility |
|--------|----------------|
| `perform_ai_market_research` | Builds Gemini prompt, injects optional **additional_criteria**, parses JSON response, returns `solution_characteristics`, `additional_criteria`, `summary_insight`, and `market_research_matrix`.
| `generate_target_companies_by_ai` | Accepts a list of solution sections, runs Gemini to produce a prioritized company list and a Venn diagram (SVG).
| `create_interview_email_draft` | Generates a cold‑outreach email using the selected company & solution description.
| `create_interview_guide_markdown` | Produces a markdown interview‑guide (agenda & questions).
| `get_company_contact_info` | Looks up contact URLs/LinkedIn for a given company.
| `runAiAnalysis` (JS front‑end call) | Calls `/api/analyze` which internally invokes `generate_target_companies_by_ai`.

All functions return plain JSON, making them easy to consume from any HTTP client.

---
## 4. UI Application (Front‑end) Overview
- **Framework**: Vanilla HTML/JavaScript (no external bundler). Uses Material Symbols for icons.
- **Key UI Elements**:
  - **Section Cards** – Dynamically added via `addSectionCard()`. Each has a **Delete** button (`btn-remove-sec`).
  - **Market Research Pane** – Textareas for **Solution Characteristics** and **Additional Criteria**. `runMarketResearch()` posts JSON to `/api/market-research` and renders a rich table (`renderMarketResearchData`).
  - **Venn Diagram Pane** – SVG injected after `/api/analyze` completes.
  - **Company Grid / Detail Tabs** – Populated from `/api/analyze` results.
- **State Management**: Simple globals (`sectionCount`, `selectedCompany`, `currentResults`). UI updates are performed directly on DOM elements.
- **Cache‑Busting**: A custom `NoCacheStaticFiles` subclass in `frontend/main.py` adds `Cache‑Control: no-store, no-cache, must-revalidate, max-age=0` to all static assets, ensuring that a hard refresh always loads the newest HTML/JS/CSS.

---
## 5. Integration / Request Flow
```
User (Browser)
   │  GET /                → FastAPI serves index.html (no‑cache headers)
   │  ↕
   │  Interacts – creates sections, fills textareas
   │  ↕
   │  POST /api/market-research  → FastAPI → app.tools.perform_ai_market_research()
   │  ↕ (JSON response)            ↓
   │  UI renders matrix & summary (renderMarketResearchData)
   │
   │  POST /api/analyze           → FastAPI → app.tools.generate_target_companies_by_ai()
   │  ↕ (JSON with company list + SVG)
   │  UI updates company grid + Venn diagram
   │
   │  Further POSTs (/api/email, /api/guide, /api/contact) follow the same pattern.
```
All communication is **stateless** HTTP POST/GET with JSON payloads, making it easy to replace the UI or call the APIs from other clients.

---
## 6. Deployment & Operations
| Step | Command (gcloud) |
|------|-------------------|
| Build & push image | `gcloud builds submit --tag us-east1-docker.pkg.dev/PROJECT/cloud-run-source-deploy/b2b-interview-strategist-ui:TAG` |
| Deploy to Cloud Run | `gcloud run deploy b2b-interview-strategist-ui --image=...:TAG --region=us-east1 --platform=managed --memory=2Gi` |
| Delete service (stop & remove) | `gcloud run services delete b2b-interview-strategist-ui --region=us-east1 --quiet` |

The service runs on **Python 3.11**, **FastAPI**, and **Uvicorn** (port 8080). No persistent storage is required – all state lives in the browser or is recomputed on each request.

---
## 7. Extensibility Points
- **Add new agent tools**: Create a function in `app/tools.py` and expose it through a new `/api/<name>` route in `frontend/main.py`.
- **Replace Gemini model**: Change the `model=` argument in `client.models.generate_content` (e.g., to `gemini-1.5-pro`).
- **Persist data**: Mount a Cloud SQL or Firestore client and store user‑generated sections if needed.
- **Authentication**: Wrap the FastAPI app with `OAuth2` or `Google IAP` to restrict access.

---
## 8. Downloadable Artifact
The design document is saved as a Markdown file that can be downloaded directly from the workspace:

[design.md](file:///C:/Users/oumar/.gemini/antigravity/brain/aa168390-4c99-4350-a99c-3aff61012c3d/design.md)

Feel free to open the file, share it, or add it to your repository.
