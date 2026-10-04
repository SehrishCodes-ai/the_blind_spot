from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class DecisionRequest(BaseModel):
    """Input payload for decision reasoning analysis."""
    decision: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="The core decision or situation being considered."
    )
    reasoning: str = Field(
        ...,
        min_length=10,
        max_length=4000,
        description="The user's current reasoning, rationale, and visible factors."
    )
    priorities: Optional[str] = Field(
        default="",
        max_length=1500,
        description="Stated goals, values, or top priorities."
    )
    constraints: Optional[str] = Field(
        default="",
        max_length=1500,
        description="External constraints, deadlines, or resource limits."
    )
    options_considered: Optional[List[str]] = Field(
        default_factory=list,
        description="List of options the user is currently weighing."
    )


class UnderstoodFact(BaseModel):
    """Categorized understanding of what the user communicated."""
    content: str
    fact_type: Literal["explicit", "inferred"] = "explicit"
    source_context: str = ""


class VisibleFactor(BaseModel):
    """A salient factor currently dominating or anchoring the user's reasoning."""
    factor: str
    why_prominent: str
    anchoring_risk: str


class BlindSpot(BaseModel):
    """A potential blind spot that is not immediately visible in the reasoning."""
    title: str
    description: str
    category: str  # e.g. "Second-Order Effects", "Opportunity Cost", "Unstated Dependency", "Hidden Cost"
    severity: Literal["critical", "significant", "moderate"] = "significant"


class Assumption(BaseModel):
    """An unstated or questionable assumption underpinning the decision."""
    assumption: str
    condition_to_hold: str  # "What would need to be true for this to hold?"
    risk_if_invalid: str


class OverlookedFactor(BaseModel):
    """A factor or consequence the user may have missed."""
    factor: str
    potential_impact: str
    dimension: str  # e.g. "Academic", "Career", "Health", "Social", "Operational"


class ConflictTension(BaseModel):
    """A friction, contradiction, or trade-off tension within the user's own reasoning."""
    title: str
    conflicting_elements: List[str]
    explanation: str


class TradeOff(BaseModel):
    """A clear trade-off inherent in the choice."""
    giving_up: str
    gaining: str
    underlying_value: str


class MissingInformation(BaseModel):
    """Data or evidence that the user should verify before deciding."""
    item_needed: str
    why_critical: str
    how_to_verify: str


class AlternativePerspective(BaseModel):
    """A different viewpoint or angle to stress-test the reasoning."""
    angle_name: str  # e.g. "Your 3-Years-From-Now Self", "A Critical Mentor", "Worst-Case Pre-Mortem"
    perspective_description: str


class ReflectiveQuestion(BaseModel):
    """A neutral, non-leading question designed to provoke critical reflection."""
    question: str
    purpose: str
    suggested_focus: str


class AnalysisResponse(BaseModel):
    """Structured response containing all blind spot insights."""
    decision_summary: str
    understanding: List[UnderstoodFact]
    most_visible_factors: List[VisibleFactor]
    potential_blind_spots: List[BlindSpot]
    assumptions_to_examine: List[Assumption]
    overlooked_factors: List[OverlookedFactor]
    conflicts_and_tensions: List[ConflictTension]
    trade_offs: List[TradeOff]
    missing_information: List[MissingInformation]
    alternative_perspectives: List[AlternativePerspective]
    reflective_questions: List[ReflectiveQuestion]
    decision_ownership_statement: str = (
        "The AI companion provides analysis to support critical thinking only. "
        "It does not recommend or choose any option. The final judgment and decision remain entirely yours."
    )
    model_provider: str = "Google Gemini"
    model_name: str = "gemini-3.8-flash"
    execution_mode: Literal["gemini", "heuristic_engine"] = "gemini"


class DeepDiveRequest(BaseModel):
    """Request for digging deeper into a specific question or assumption."""
    decision: str
    selected_question_or_assumption: str
    user_reflection: str


class DeepDiveResponse(BaseModel):
    """Thinking companion's response to user reflection without making decisions."""
    topic: str
    reflective_mirror: str
    tensions_surfaced: List[str]
    probing_follow_up_questions: List[str]
    reminder: str = "This analysis aims to expand your perspective; the final decision is yours alone."
