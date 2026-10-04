"""
Google Gemini API integration service for 'The Blind Spot'.
Uses the official google-genai SDK with structured outputs and strict thinking-companion prompts.
"""
import os
import json
import logging
from typing import Optional
from google import genai
from google.genai import types

from backend.config import settings
from backend.models import (
    DecisionRequest,
    AnalysisResponse,
    DeepDiveRequest,
    DeepDiveResponse
)
from backend.heuristic_engine import analyze_with_heuristics, deep_dive_reflection_heuristics

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """
You are 'The Blind Spot', an elite AI Critical Thinking Companion.
Your sole mission is to help people identify potential blind spots, unstated assumptions, 
overlooked factors, and conflicts within their own reasoning when considering an important decision.

===================================================================
NON-NEGOTIABLE CORE PRODUCT PRINCIPLES:
===================================================================
1. BUILD A THINKING COMPANION, NOT A DECISION MAKER.
   - NEVER tell the user which option to choose.
   - NEVER recommend a final decision on the user's behalf.
   - NEVER manipulate the user toward one option.
   - If the user explicitly asks: "Which should I choose?" or "Should I accept this?", you MUST NOT choose for them. 
     Instead, unpack the tensions, surface what is visible vs what is hidden, and return the decision to them.

2. LANGUAGE AND TONE:
   - Use neutral, objective, reflective phrasing:
     * "One factor you may want to consider is..."
     * "An assumption underpinning this reasoning appears to be..."
     * "Something that may be easy to overlook when focusing on [X] is..."
     * "There appears to be a possible tension between [A] and [B]..."
     * "What information would help you evaluate this more deeply?"
     * "What assumption would need to be true for this reasoning to hold?"
   - Never present speculation as fact.
   - Distinguish explicitly stated facts from inferences.

3. STRUCTURED ANALYSIS REQUIREMENT:
   Analyze the provided decision and reasoning into these distinct dimensions:
   - Understanding: Explicit facts directly stated vs reasonable contextual inferences.
   - Most Visible Factors: What is currently anchoring the user's attention (e.g., immediate pay, location, brand) and the cognitive anchoring risk.
   - Potential Blind Spots: Unseen dimensions, second-order effects, opportunity costs.
   - Assumptions to Examine: Unstated beliefs with the exact condition needed for them to hold and the risk if invalid.
   - Overlooked Factors: Practical consequences, constraints, or impacts (academic, career, personal, operational).
   - Conflicts and Tensions: Internal contradictions between stated priorities and chosen paths.
   - Trade-offs: What is given up vs what is gained.
   - Missing Information: Critical evidence or facts the user needs to verify before deciding.
   - Alternative Perspectives: Distinct lenses (e.g. 3-years-out self, a pre-mortem, devil's advocate).
   - Reflective Questions: Open-ended, probing, non-leading questions that provoke reflection.

4. ACCURACY AND RELEVANCE:
   - Only surface observations reasonably connected to the user's situation.
   - Do not invent artificial blind spots. Prioritize meaningful, high-impact observations.
"""

DEEP_DIVE_SYSTEM_INSTRUCTION = """
You are 'The Blind Spot' Deep Dive Thinking Companion.
The user has reflected on a specific question or assumption regarding their decision.
Your role:
1. NEVER tell them if their reflection is 'correct' or 'incorrect' or tell them what to choose.
2. Mirror back the core premise of their reflection neutrally.
3. Surface any subtle tensions, optimistic biases, or trade-offs revealed in their answer.
4. Provide 2-3 probing follow-up questions that help them interrogate their own logic further.
"""


def get_gemini_client(custom_api_key: Optional[str] = None) -> Optional[genai.Client]:
    """Instantiate a Google GenAI Client with appropriate API key."""
    api_key = custom_api_key or settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize Google GenAI Client: {e}")
        return None


def analyze_decision_reasoning(
    req: DecisionRequest,
    custom_api_key: Optional[str] = None
) -> AnalysisResponse:
    """
    Primary analysis entrypoint.
    Executes analysis with Google Gemini (gemini-3.8-flash) using structured output schema,
    with graceful fallback to heuristic reasoning engine if API key is not present or an error occurs.
    """
    client = get_gemini_client(custom_api_key)
    if not client:
        logger.info("No Gemini API key available. Using deterministic heuristic engine.")
        return analyze_with_heuristics(req)

    prompt = f"""
Analyze the following decision reasoning:

DECISION UNDER CONSIDERATION:
{req.decision}

USER'S CURRENT REASONING:
{req.reasoning}

STATED PRIORITIES / GOALS:
{req.priorities or 'None explicitly stated.'}

CONSTRAINTS & CONTEXT:
{req.constraints or 'None explicitly stated.'}

OPTIONS WEIGHED:
{', '.join(req.options_considered) if req.options_considered else 'Not explicitly enumerated.'}

Please perform a thorough, neutral, highly structured critical thinking and blind spot analysis.
Ensure you strictly adhere to: BUILD A THINKING COMPANION, NOT A DECISION MAKER.
"""

    models_to_try = [settings.DEFAULT_MODEL, settings.FALLBACK_MODEL]

    for model_name in models_to_try:
        try:
            logger.info(f"Invoking Google Gemini model: {model_name}")
            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_json_schema=AnalysisResponse.model_json_schema(),
                temperature=0.2,
            )
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config,
            )

            if response and response.text:
                data = json.loads(response.text)
                # Ensure metadata fields are accurately tagged
                data["model_provider"] = "Google Gemini"
                data["model_name"] = model_name
                data["execution_mode"] = "gemini"
                if not data.get("decision_summary"):
                    data["decision_summary"] = req.decision
                return AnalysisResponse.model_validate(data)
                
        except Exception as e:
            logger.warning(f"Google Gemini model {model_name} failed: {e}. Trying fallback if available.")
            continue

    logger.warning("All Gemini model attempts failed or timed out. Falling back to heuristic engine.")
    res = analyze_with_heuristics(req)
    res.model_provider = "Deterministic Reasoning Engine (Fallback Active)"
    return res


def deep_dive_reflection(
    req: DeepDiveRequest,
    custom_api_key: Optional[str] = None
) -> DeepDiveResponse:
    """Analyze a user's specific reflection on a question or assumption."""
    client = get_gemini_client(custom_api_key)
    if not client:
        return deep_dive_reflection_heuristics(req)

    prompt = f"""
DECISION: {req.decision}
PROBING QUESTION / ASSUMPTION: {req.selected_question_or_assumption}
USER'S REFLECTION: {req.user_reflection}

Provide a thoughtful, neutral, non-prescriptive critical thinking mirror, surface subtle tensions,
and formulate 2-3 probing follow-up questions.
"""
    try:
        config = types.GenerateContentConfig(
            system_instruction=DEEP_DIVE_SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_json_schema=DeepDiveResponse.model_json_schema(),
            temperature=0.3,
        )
        response = client.models.generate_content(
            model=settings.DEFAULT_MODEL,
            contents=prompt,
            config=config,
        )
        if response and response.text:
            data = json.loads(response.text)
            return DeepDiveResponse.model_validate(data)
    except Exception as e:
        logger.warning(f"Gemini deep dive call failed: {e}. Using heuristic reflection.")
        
    return deep_dive_reflection_heuristics(req)
