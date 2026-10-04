"""
FastAPI Application for 'The Blind Spot'
Exposes REST endpoints for critical-thinking analysis, scenarios, and deep dive reflection,
and serves the static web UI.
"""
import os
import logging
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Request, Header, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from backend.config import settings
from backend.models import (
    DecisionRequest,
    AnalysisResponse,
    DeepDiveRequest,
    DeepDiveResponse
)
from backend.gemini_service import analyze_decision_reasoning, deep_dive_reflection
from backend.scenarios import get_all_scenarios, get_scenario_by_id

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("blind_spot_app")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Critical Thinking Companion that surfaces blind spots, assumptions, and tensions without deciding for the user."
)

# Enable CORS for local development and testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Clean validation error response without leaking internals."""
    errors = []
    for err in exc.errors():
        field = " -> ".join([str(loc) for loc in err.get("loc", [])])
        msg = err.get("msg", "Invalid input value.")
        errors.append(f"{field}: {msg}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Please review the submitted decision and reasoning.",
            "details": errors
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Global exception handler to avoid leaking stack traces."""
    logger.error(f"Unhandled exception during request {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Error",
            "message": "An unexpected error occurred while analyzing the reasoning. Please try again."
        }
    )


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health_check() -> Dict[str, Any]:
    """Health check endpoint indicating service status and Gemini availability."""
    has_api_key = bool(settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "gemini_api_configured": has_api_key,
        "default_model": settings.DEFAULT_MODEL,
        "fallback_model": settings.FALLBACK_MODEL,
        "mode": "production"
    }


@app.get("/api/scenarios")
def list_scenarios() -> List[Dict[str, Any]]:
    """Retrieve preloaded test scenarios."""
    return get_all_scenarios()


@app.get("/api/scenarios/{scenario_id}")
def get_scenario(scenario_id: str) -> Dict[str, Any]:
    """Retrieve a single scenario by ID."""
    return get_scenario_by_id(scenario_id)


@app.post("/api/analyze", response_model=AnalysisResponse)
def analyze_reasoning(
    payload: DecisionRequest,
    x_gemini_api_key: Optional[str] = Header(None, description="Optional runtime Gemini API key")
) -> AnalysisResponse:
    """
    Analyze user decision reasoning to surface blind spots, assumptions,
    trade-offs, overlooked factors, and reflective questions.
    """
    if not payload.decision.strip() or len(payload.decision.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The decision statement must be at least 3 characters long."
        )
    if not re.search(r'\p{L}', payload.decision, re.UNICODE) if False else not re.search(r'[^\W\d_]', payload.decision, re.UNICODE):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The decision statement must contain at least some text (not only numbers or symbols)."
        )
    if not payload.reasoning.strip() or len(payload.reasoning.strip()) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide at least 10 characters explaining your current reasoning."
        )
    if not re.search(r'[^\W\d_]', payload.reasoning, re.UNICODE):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The reasoning must contain at least some text (not only numbers or symbols)."
        )

    # Perform analysis
    result = analyze_decision_reasoning(payload, custom_api_key=x_gemini_api_key)
    return result


@app.post("/api/deep-dive", response_model=DeepDiveResponse)
def deep_dive(
    payload: DeepDiveRequest,
    x_gemini_api_key: Optional[str] = Header(None, description="Optional runtime Gemini API key")
) -> DeepDiveResponse:
    """
    Deep-dive reflection endpoint that helps user interrogate their own thinking
    on a selected question or assumption.
    """
    if not payload.user_reflection.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reflection text cannot be empty."
        )
    return deep_dive_reflection(payload, custom_api_key=x_gemini_api_key)


# ---------------------------------------------------------------------------
# Frontend Static Asset Mounting
# ---------------------------------------------------------------------------
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/")
    def serve_frontend_index():
        index_file = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "Frontend index.html not found."}
