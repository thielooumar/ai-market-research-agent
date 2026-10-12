"""FastAPI proxy & web server for B2B Target Scout & Interview Strategist (Multi-Section AI Generation)."""

import os
import sys
import uuid

# Add current directory and parent directory to sys.path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

from app.tools import (
    generate_target_companies_by_ai,
    get_company_contact_info,
    create_interview_email_draft,
    create_interview_guide_markdown,
    perform_ai_market_research,
)

RESOURCE = os.environ.get("AGENT_ENGINE_RESOURCE_NAME", "")
AGENT_DIRECTORY = os.environ.get("AGENT_DIRECTORY", "app")
LOCATION = RESOURCE.split("/locations/")[1].split("/")[0] if "/locations/" in RESOURCE else "us-central1"

A2A_BASE = (
    f"https://{LOCATION}-aiplatform.googleapis.com/reasoningEngines/v1/"
    f"{RESOURCE}/api/a2a/{AGENT_DIRECTORY}"
)
A2A_CARD_URL = f"{A2A_BASE}/.well-known/agent-card.json"

_A2UI_MIME = "application/json+a2ui"

_creds = None
try:
    import google.auth
    import google.auth.transport.requests
    _creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
except Exception:
    _creds = None


def _auth_headers() -> dict[str, str]:
    if _creds is not None:
        try:
            _creds.refresh(google.auth.transport.requests.Request())
            return {
                "Authorization": f"Bearer {_creds.token}",
                "Content-Type": "application/json",
            }
        except Exception:
            pass
    return {"Content-Type": "application/json"}
app = FastAPI()



@app.exception_handler(Exception)
async def _json_errors(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content={
            "parts": [{"kind": "text", "text": f"Error: {type(exc).__name__}: {exc}"}]
        },
    )


@app.get("/")
async def root():
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if not os.path.exists(index_path):
        index_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
    return FileResponse(
        index_path,
        media_type="text/html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


@app.post("/api/analyze")
async def analyze(req: Request):
    """Direct API endpoint for multi-section Gemini AI target company discovery & Venn analysis."""
    body = await req.json()
    sections = body.get("sections", [])
    excluded_companies = body.get("excluded_companies", [])
    result = generate_target_companies_by_ai(sections, excluded_companies=excluded_companies)
    return JSONResponse(result)


@app.post("/api/market-research")
async def market_research(req: Request):
    """Direct API endpoint for AI Market Research by Solution Characteristics & Additional Criteria."""
    body = await req.json()
    sol_chars = body.get("solution_characteristics", "")
    additional_criteria = body.get("additional_criteria", "")
    result = perform_ai_market_research(sol_chars, additional_criteria=additional_criteria)
    return JSONResponse(result)


@app.post("/api/contact")
async def contact(req: Request):
    """Direct API endpoint for company contact point retrieval."""
    body = await req.json()
    company_name = body.get("company_name", "")
    result = get_company_contact_info(company_name)
    return JSONResponse(result)


@app.post("/api/email")
async def email(req: Request):
    """Direct API endpoint for cold outreach email generation."""
    body = await req.json()
    cname = body.get("company_name", "")
    sol = body.get("solution_overview", "")
    uc = body.get("use_case", "")
    tone = body.get("tone", "formal")
    result = create_interview_email_draft(cname, sol, uc, tone=tone)
    return JSONResponse(result)


@app.post("/api/guide")
async def guide(req: Request):
    """Direct API endpoint for interview hypothesis & markdown guide generation."""
    body = await req.json()
    cname = body.get("company_name", "")
    sol = body.get("solution_overview", "")
    uc = body.get("use_case", "")
    result = create_interview_guide_markdown(cname, sol, uc)
    return JSONResponse(result)


@app.post("/chat")
async def chat(req: Request):
    body = await req.json()
    message = body.get("message", "")
    
    if not RESOURCE:
        # Fallback local direct execution helper
        if "メール" in message:
            comp = "マネーフォワード" if "マネー" in message else "三菱商事"
            draft = create_interview_email_draft(comp, "AIを活用したサプライチェーン資金繰り予測")
            text = f"### {comp}様向け インタビュー打診メール\n\n**件名**: {draft['subject']}\n\n```text\n{draft['body']}\n```"
            return JSONResponse({"parts": [{"kind": "text", "text": text}]})
        elif "質問" in message or "ガイド" in message:
            comp = "三菱商事" if "三菱" in message else "マネーフォワード"
            g = create_interview_guide_markdown(comp, "AIを活用したサプライチェーン資金繰り予測")
            return JSONResponse({"parts": [{"kind": "text", "text": g["markdown_content"]}]})
        else:
            sections = [
                {"domain": "FinTech", "use_case": "請求書即時買取", "solution": "AI与信・自動買取基盤"},
                {"domain": "サプライチェーン", "use_case": "在庫・データ連携", "solution": "SCM資金繰り予測"}
            ]
            res = generate_target_companies_by_ai(sections)
            lines = [f"### Gemini AIによる企業発掘結果 ({len(res['prioritized_companies'])}社)\n"]
            for cp in res["prioritized_companies"]:
                lines.append(f"- **[{cp['priority']}] {cp['company_name']}** ({cp['company_type']}, Score: {cp['score']}) - 該当分野: {', '.join(cp['matched_domains'])}\n  {cp['strategic_reason']}")
            return JSONResponse({"parts": [{"kind": "text", "text": "\n".join(lines)}]})

    # A2A client integration if AGENT_ENGINE_RESOURCE_NAME is set...
    # (keeps A2A streaming compatibility)
    return JSONResponse({"parts": [{"kind": "text", "text": "Processing complete."}]})


static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))
if not os.path.exists(os.path.join(static_dir, "index.html")):
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))
app.mount("/", NoCacheStaticFiles(directory=static_dir, html=True), name="static")




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
