"""
Heuristic & Deterministic Fallback Engine for 'The Blind Spot'
Provides robust, structured reasoning analysis even in offline/mock conditions or
when Gemini API key is unavailable or throttled.
"""
import re
from typing import List
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
    DeepDiveRequest,
    DeepDiveResponse
)


def analyze_with_heuristics(req: DecisionRequest) -> AnalysisResponse:
    """Analyze decision reasoning using rule-based heuristics and NLP pattern recognition."""
    combined_text = f"{req.decision} {req.reasoning} {req.priorities or ''} {req.constraints or ''}".lower()
    
    # 1. Distinguish Explicit facts vs Inferences
    understanding: List[UnderstoodFact] = []
    
    # Split reasoning into sentences or clauses
    raw_sentences = [s.strip() for s in re.split(r'[.;\n]+', req.reasoning) if len(s.strip()) > 6]
    for s in raw_sentences[:4]:
        understanding.append(
            UnderstoodFact(
                content=f"You stated: \"{s}\"",
                fact_type="explicit",
                source_context="Provided directly in your reasoning statement."
            )
        )
    
    if req.priorities:
        understanding.append(
            UnderstoodFact(
                content=f"Stated priority / goal: \"{req.priorities.strip()}\"",
                fact_type="explicit",
                source_context="Extracted from your stated priorities."
            )
        )
    
    if req.constraints:
        understanding.append(
            UnderstoodFact(
                content=f"Stated constraints: \"{req.constraints.strip()}\"",
                fact_type="explicit",
                source_context="Extracted from your stated constraints."
            )
        )
        
    understanding.append(
        UnderstoodFact(
            content="You appear to be actively weighing immediate tangible benefits against future potential.",
            fact_type="inferred",
            source_context="Inferred from the emphasis placed on current visible benefits."
        )
    )

    # 2. Identify Most Visible Factors (Anchoring)
    visible_factors: List[VisibleFactor] = []
    
    if any(k in combined_text for k in ["stipend", "salary", "money", "pay", "cost", "price", "compensation"]):
        visible_factors.append(
            VisibleFactor(
                factor="Financial compensation or immediate cost",
                why_prominent="Financial figures are concrete, numerical, and immediately measurable, making them natural cognitive anchors.",
                anchoring_risk="May overshadow non-monetary costs like skill stagnation, high stress, or academic derailment."
            )
        )
        
    if any(k in combined_text for k in ["close", "near", "location", "commute", "remote", "distance", "office"]):
        visible_factors.append(
            VisibleFactor(
                factor="Geographical convenience / proximity",
                why_prominent="Convenience and minimal travel time provide immediate daily friction reduction.",
                anchoring_risk="A convenient location does not guarantee high mentorship, cultural fit, or career momentum."
            )
        )
        
    if any(k in combined_text for k in ["experience", "resume", "cv", "brand", "prestige", "name"]):
        visible_factors.append(
            VisibleFactor(
                factor="Resume branding & industry experience",
                why_prominent="Having a formal credential or title is a high-visibility signal to external observers.",
                anchoring_risk="Assumes any experience on paper translates into genuine skill acquisition and demonstrable growth."
            )
        )
        
    if not visible_factors:
        visible_factors.append(
            VisibleFactor(
                factor="Immediate, easily measurable outcomes",
                why_prominent="The current rationale highlights short-term tangible metrics over long-term qualitative shifts.",
                anchoring_risk="Risk of neglecting subtle cumulative consequences that compound over time."
            )
        )

    # 3. Detect Potential Blind Spots
    blind_spots: List[BlindSpot] = []
    
    # Check for Internship / College domain
    if any(k in combined_text for k in ["intern", "internship", "college", "semester", "academic", "gpa", "study"]):
        blind_spots.append(
            BlindSpot(
                title="Academic Dilution & Cognitive Fatigue",
                description="Managing substantial external commitments alongside coursework often leads to cognitive fatigue rather than balanced productivity.",
                category="Second-Order Effects",
                severity="critical"
            )
        )
        blind_spots.append(
            BlindSpot(
                title="Actual Learning vs. Routine Operational Labor",
                description="Internships and entry roles frequently promise 'industry experience' but may relegate students to low-context, repetitive execution without structured mentorship.",
                category="Information Gap",
                severity="critical"
            )
        )
        blind_spots.append(
            BlindSpot(
                title="Opportunity Cost of Alternative Skill-Building",
                description="Time allocated here cannot be spent building independent portfolio projects, contributing to deep research, or preparing for high-bar competitive interviews.",
                category="Opportunity Cost",
                severity="significant"
            )
        )
    elif any(k in combined_text for k in ["startup", "corporate", "job", "career", "company", "switch"]):
        blind_spots.append(
            BlindSpot(
                title="True Mentorship & Feedback Bandwidth",
                description="The prestige or agility of the workplace does not reveal whether senior staff actually have dedicated hours to invest in your development.",
                category="Operational Reality",
                severity="critical"
            )
        )
        blind_spots.append(
            BlindSpot(
                title="Reversibility and Exit Options",
                description="Evaluating a transition without planning an exit ramp or checking how the industry views this specific detour.",
                category="Strategic Flexibility",
                severity="significant"
            )
        )
    else:
        blind_spots.append(
            BlindSpot(
                title="Underestimating Ongoing Maintenance & Friction",
                description="Initial choices rarely remain static; the ongoing energy required to sustain this decision often exceeds the initial setup cost.",
                category="Hidden Cost",
                severity="critical"
            )
        )
        blind_spots.append(
            BlindSpot(
                title="Survivorship Bias in Expected Upside",
                description="Relying on idealized success cases while ignoring the default operational frictions inherent to this path.",
                category="Cognitive Bias",
                severity="significant"
            )
        )

    # 4. Assumptions to Examine
    assumptions: List[Assumption] = []
    assumptions.append(
        Assumption(
            assumption="The external organization or situation will match its advertised or intended promises.",
            condition_to_hold="You must have direct verification from past participants or current peers, not just the official pitch.",
            risk_if_invalid="You may expend 3 to 6 months in an environment that fails to deliver expected growth."
        )
    )
    assumptions.append(
        Assumption(
            assumption="Energy levels and focus will remain consistent across parallel commitments.",
            condition_to_hold="You have previously sustained an identical workload without a drop in quality, health, or GPA.",
            risk_if_invalid="Burnout, compromised grades, or substandard performance in both arenas."
        )
    )
    assumptions.append(
        Assumption(
            assumption="The visible advantages (e.g. stipend, location) outweigh the unseen trade-offs.",
            condition_to_hold="Your primary 2-year goal is served more by these immediate perks than by alternative paths.",
            risk_if_invalid="Short-term convenience achieved at the expense of long-term strategic trajectory."
        )
    )

    # 5. Overlooked Factors
    overlooked: List[OverlookedFactor] = []
    if "college" in combined_text or "academic" in combined_text or "study" in combined_text:
        overlooked.append(
            OverlookedFactor(
                factor="Impact on Academic Standing & Exam Windows",
                potential_impact="Attendance deficits, assignment crunches, and reduced preparation during midterms and finals.",
                dimension="Academic"
            )
        )
        overlooked.append(
            OverlookedFactor(
                factor="Mentorship Quality and Engineering Rigor",
                potential_impact="Without dedicated senior guidance, self-learning may be slower than structured independent study.",
                dimension="Professional Growth"
            )
        )
    overlooked.append(
        OverlookedFactor(
            factor="Energy & Psychological Reserve for High-Leverage Opportunities",
            potential_impact="Being constantly drained leaves zero slack to seize unexpected career breaks or critical networking.",
            dimension="Psychological & Energy Slack"
        )
    )
    overlooked.append(
        OverlookedFactor(
            factor="Alignment with Long-Term (2-3 Year) Career Milestones",
            potential_impact="Building credibility in a domain or technology stack you may not actually want to specialize in.",
            dimension="Strategic Positioning"
        )
    )

    # 6. Possible Conflicts / Tensions
    conflicts: List[ConflictTension] = []
    if any(k in combined_text for k in ["gpa", "study", "exam", "grade", "classes", "attendance"]):
        conflicts.append(
            ConflictTension(
                title="Tension Between Academic Excellence and Industry Immersion",
                conflicting_elements=[
                    "Desire to maintain high grades and meet university obligations",
                    "Commitment to fixed working hours and workplace delivery deadlines"
                ],
                explanation="Both demand peak cognitive attention; when simultaneous deadlines collide, one will inevitably be compromised."
            )
        )
    conflicts.append(
        ConflictTension(
            title="Short-Term Convenience vs. Peak Growth Potential",
            conflicting_elements=[
                "Choosing based on proximity, ease of access, and immediate cash",
                "Long-term ambition for high-tier technical mastery and prestigious career leaps"
            ],
            explanation="The easiest option to start is often not the option with the highest growth ceiling."
        )
    )

    # 7. Trade-offs
    trade_offs: List[TradeOff] = [
        TradeOff(
            giving_up="Discretionary time, academic focus, and cognitive rest",
            gaining="Practical exposure, routine workplace immersion, and direct compensation",
            underlying_value="Cash and early resume bullet point vs. deep learning and academic peace of mind"
        ),
        TradeOff(
            giving_up="Flexibility to pivot or work on personalized open-source / research projects",
            gaining="Structured corporate schedule and external accountability",
            underlying_value="Autonomy and self-directed mastery vs. externally enforced routine"
        )
    ]

    # 8. Missing Information
    missing_info: List[MissingInformation] = [
        MissingInformation(
            item_needed="Verifiable day-to-day task breakdown from former or current team members",
            why_critical="Prevents surprise realization that the role consists primarily of low-level busywork or outdated tools.",
            how_to_verify="Reach out to 2 past interns or current junior employees via LinkedIn with 3 specific questions."
        ),
        MissingInformation(
            item_needed="Formal institutional policy on attendance, attendance grace limits, and exam clash leave",
            why_critical="Avoids unexpected academic disqualification or hostile workplace ultimatums during finals.",
            how_to_verify="Check department handbook and obtain written confirmation from department head / manager."
        ),
        MissingInformation(
            item_needed="Clear definition of mentorship commitment (e.g., weekly 1-on-1s, code reviews)",
            why_critical="Ensures you are not left to sink or swim without feedback.",
            how_to_verify="Ask the hiring lead or engineering manager during pre-acceptance inquiry."
        )
    ]

    # 9. Alternative Perspectives
    perspectives: List[AlternativePerspective] = [
        AlternativePerspective(
            angle_name="Your 3-Years-From-Now Self",
            perspective_description="Looking back, will the stipend amount matter, or will the depth of the technologies you touched and the caliber of your mentors be the deciding differentiator?"
        ),
        AlternativePerspective(
            angle_name="The Pre-Mortem (Assuming Regret in 4 Months)",
            perspective_description="Imagine it is 4 months in: you are exhausted, grades are slipping, and the work is mundane. What was the exact unexamined assumption that led here?"
        ),
        AlternativePerspective(
            angle_name="The Independent Builder Lens",
            perspective_description="If you treated the next 6 months as a self-directed fellowship to build 2 end-to-end ambitious systems, would your growth surpass this role?"
        )
    ]

    # 10. Questions to Consider (Reflective, Non-Leading)
    questions: List[ReflectiveQuestion] = [
        ReflectiveQuestion(
            question="What evidence do you currently possess that proves this role will offer meaningful mentorship rather than repetitive execution?",
            purpose="Examine the foundation of your learning assumption.",
            suggested_focus="Mentorship vs Task Execution"
        ),
        ReflectiveQuestion(
            question="If the stipend were zero, how compelling would the learning and networking aspects of this opportunity remain to you?",
            purpose="Isolate the financial anchor from the developmental merit.",
            suggested_focus="Separating Cash from Growth"
        ),
        ReflectiveQuestion(
            question="What is your non-negotiable threshold for your academic grades, and what specific contingency plan will you trigger if coursework falls behind?",
            purpose="Anticipate practical friction before commitments become binding.",
            suggested_focus="Stress-Testing Academic Limits"
        ),
        ReflectiveQuestion(
            question="What specific skill or outcome must you achieve during these months for you to look back and consider this decision an undeniable success?",
            purpose="Define internal success criteria independently of external validation.",
            suggested_focus="Defining Concrete Success Metrics"
        )
    ]

    return AnalysisResponse(
        decision_summary=req.decision,
        understanding=understanding,
        most_visible_factors=visible_factors,
        potential_blind_spots=blind_spots,
        assumptions_to_examine=assumptions,
        overlooked_factors=overlooked,
        conflicts_and_tensions=conflicts,
        trade_offs=trade_offs,
        missing_information=missing_info,
        alternative_perspectives=perspectives,
        reflective_questions=questions,
        decision_ownership_statement=(
            "This analysis is designed solely to expand your perspective and illuminate blind spots. "
            "It deliberately avoids advising you on what to choose. The final evaluation, judgment, "
            "and decision are 100% yours."
        ),
        model_provider="Deterministic Reasoning Engine",
        model_name="heuristic-engine-v1",
        execution_mode="heuristic_engine"
    )


def deep_dive_reflection_heuristics(req: DeepDiveRequest) -> DeepDiveResponse:
    """Provide structured, reflective follow-up on a specific question without taking a side."""
    reflection_lower = req.user_reflection.lower()
    
    tensions: List[str] = []
    follow_ups: List[str] = []
    
    if any(k in reflection_lower for k in ["i think", "probably", "should be fine", "manage", "somehow", "hope"]):
        tensions.append("Your reflection relies partly on optimistic forecasting ('should be fine') rather than concrete operational proof.")
        follow_ups.append("What is one concrete metric or boundary that would signal to you that things are no longer 'fine'?")
        follow_ups.append("How would you respond if that boundary is crossed in week 3?")
    else:
        tensions.append("Notice which priority you naturally defended first in your answer.")
        follow_ups.append("What assumption would have to be false for this priority to lose its importance?")
        follow_ups.append("What would a peer who values the opposite choice say in response to your reflection?")
        
    follow_ups.append("What missing piece of data would turn this uncertainty into a well-grounded assessment?")

    mirror = (
        f"In reflecting on '{req.selected_question_or_assumption}', you emphasized: "
        f"\"{req.user_reflection[:140]}...\". This reveals where your instinct leans, while also "
        "highlighting the balance between optimism and practical constraints."
    )
    
    return DeepDiveResponse(
        topic=req.selected_question_or_assumption,
        reflective_mirror=mirror,
        tensions_surfaced=tensions,
        probing_follow_up_questions=follow_ups,
        reminder="The AI does not decide for you. Weigh these questions against your core values to make your own decision."
    )
