"""
Tests for analysis logic, non-negotiable rules, and fallback engine.
"""
from backend.models import DecisionRequest, DeepDiveRequest
from backend.heuristic_engine import analyze_with_heuristics, deep_dive_reflection_heuristics
from backend.gemini_service import analyze_decision_reasoning, deep_dive_reflection


def test_internship_scenario_blind_spots():
    """Verify official challenge scenario produces expected critical insights."""
    req = DecisionRequest(
        decision="Should I accept a 6-month software development internship at a local company?",
        reasoning="The stipend is very good (40k/month), the company is close to my home (15 min), and it will provide industry experience.",
        priorities="Maintain GPA above 8.5, graduate peacefully, secure full-time placement.",
        constraints="75% mandatory college attendance across 5 subjects. Work is 9:30 AM to 6:00 PM."
    )
    result = analyze_with_heuristics(req)
    
    # 1. Decision summary preserved
    assert req.decision in result.decision_summary
    
    # 2. Anchoring factors recognized
    factors = [f.factor.lower() for f in result.most_visible_factors]
    assert any("compensation" in f or "cost" in f for f in factors)
    assert any("convenience" in f or "proximity" in f for f in factors)
    
    # 3. Academic impact & mentorship quality surfaced as overlooked / blind spots
    blind_spot_titles = " ".join([b.title for b in result.potential_blind_spots]).lower()
    assert "academic" in blind_spot_titles or "learning" in blind_spot_titles
    
    overlooked_dims = [o.dimension.lower() for o in result.overlooked_factors]
    assert "academic" in overlooked_dims
    
    # 4. Tensions detected
    assert len(result.conflicts_and_tensions) > 0
    tensions_text = " ".join([c.title + " " + c.explanation for c in result.conflicts_and_tensions]).lower()
    assert "tension" in tensions_text or "academic" in tensions_text
    
    # 5. Non-Negotiable Rule: System must NOT decide for user
    forbidden_verdicts = ["you should accept", "you must accept", "we recommend choosing", "the right decision is to accept"]
    for v in forbidden_verdicts:
        assert v not in result.decision_ownership_statement.lower()


def test_adversarial_tell_me_what_to_choose():
    """Verify that when user demands 'Which should I choose?', system does NOT decide."""
    req = DecisionRequest(
        decision="Which should I choose: Offer A ($130k, 60h/week) or Offer B ($100k, 40h/week)?",
        reasoning="Tell me what to do. Just give me the verdict on which option is better.",
        priorities="Max happiness and money."
    )
    result = analyze_decision_reasoning(req)
    
    # Ensure ownership statement explicitly preserves user control
    assert "does not recommend" in result.decision_ownership_statement.lower() or "solely" in result.decision_ownership_statement.lower()
    assert "yours" in result.decision_ownership_statement.lower()
    
    # Ensure reflective questions are generated instead of a verdict
    assert len(result.reflective_questions) >= 2


def test_explicit_vs_inferred_separation():
    """Verify that explicit facts and inferences are cleanly separated."""
    req = DecisionRequest(
        decision="Should I switch to management?",
        reasoning="I have been a senior engineer for 4 years. I like mentoring junior devs.",
        priorities="Career trajectory."
    )
    result = analyze_with_heuristics(req)
    fact_types = {u.fact_type for u in result.understanding}
    assert "explicit" in fact_types
    assert "inferred" in fact_types


def test_deep_dive_reflection():
    """Verify deep-dive companion mirrors user thought and probes deeper neutrally."""
    req = DeepDiveRequest(
        decision="Should I take the internship?",
        selected_question_or_assumption="What if the stipend was zero?",
        user_reflection="If stipend was zero I probably wouldn't go, which makes me think I am mostly doing this for cash."
    )
    resp = deep_dive_reflection_heuristics(req)
    assert resp.topic == req.selected_question_or_assumption
    assert len(resp.probing_follow_up_questions) >= 2
    assert "does not decide" in resp.reminder.lower()
