"""
Tests for Pydantic data models and schemas.
"""
import pytest
from pydantic import ValidationError
from backend.models import (
    DecisionRequest,
    AnalysisResponse,
    UnderstoodFact,
    VisibleFactor,
    BlindSpot,
    Assumption,
    OverlookedFactor,
    ConflictTension,
    TradeOff,
    MissingInformation,
    AlternativePerspective,
    ReflectiveQuestion,
    DeepDiveRequest
)


def test_decision_request_valid():
    """Verify valid DecisionRequest instantiates properly."""
    req = DecisionRequest(
        decision="Should I accept this software internship?",
        reasoning="Good stipend and short distance from my home.",
        priorities="Maintain GPA above 8.5",
        constraints="75% college attendance required"
    )
    assert req.decision == "Should I accept this software internship?"
    assert "stipend" in req.reasoning
    assert req.priorities == "Maintain GPA above 8.5"


def test_decision_request_empty_decision():
    """Verify empty decision triggers validation error."""
    with pytest.raises(ValidationError):
        DecisionRequest(decision="", reasoning="Reasoning is long enough here.")


def test_decision_request_short_reasoning():
    """Verify reasoning under 10 chars triggers validation error."""
    with pytest.raises(ValidationError):
        DecisionRequest(decision="Valid decision?", reasoning="Too short")


def test_decision_request_max_length_exceeded():
    """Verify extreme decision length triggers error."""
    with pytest.raises(ValidationError):
        DecisionRequest(decision="x" * 501, reasoning="Valid reasoning here for testing.")


def test_analysis_response_schema():
    """Verify AnalysisResponse enforces all required structured sections."""
    resp = AnalysisResponse(
        decision_summary="Test Decision",
        understanding=[
            UnderstoodFact(content="Explicit fact", fact_type="explicit", source_context="Direct quote")
        ],
        most_visible_factors=[
            VisibleFactor(factor="Pay", why_prominent="High number", anchoring_risk="Ignores hours")
        ],
        potential_blind_spots=[
            BlindSpot(title="Fatigue", description="Risk of burnout", category="Health", severity="critical")
        ],
        assumptions_to_examine=[
            Assumption(assumption="Work will be fun", condition_to_hold="Evidence exists", risk_if_invalid="Regret")
        ],
        overlooked_factors=[
            OverlookedFactor(factor="Academics", potential_impact="Grades slip", dimension="Academic")
        ],
        conflicts_and_tensions=[
            ConflictTension(title="Study vs Work", conflicting_elements=["Exams", "40hrs"], explanation="Tension")
        ],
        trade_offs=[
            TradeOff(giving_up="Free time", gaining="Money", underlying_value="Cash vs Rest")
        ],
        missing_information=[
            MissingInformation(item_needed="Weekly hours policy", why_critical="Overtime risk", how_to_verify="Ask HR")
        ],
        alternative_perspectives=[
            AlternativePerspective(angle_name="Future Self", perspective_description="Will it matter in 3 years?")
        ],
        reflective_questions=[
            ReflectiveQuestion(question="What if stipend was zero?", purpose="Test interest", suggested_focus="Growth")
        ]
    )
    assert resp.decision_summary == "Test Decision"
    assert "The AI companion provides analysis" in resp.decision_ownership_statement
    assert resp.understanding[0].fact_type == "explicit"
