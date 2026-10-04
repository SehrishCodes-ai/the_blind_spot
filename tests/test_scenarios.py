"""
Tests to verify all preloaded scenarios execute through analysis without issue.
"""
from backend.scenarios import get_all_scenarios
from backend.models import DecisionRequest
from backend.heuristic_engine import analyze_with_heuristics


def test_all_scenarios_execute_cleanly():
    """Verify each preloaded scenario analyzes cleanly without error."""
    scenarios = get_all_scenarios()
    assert len(scenarios) >= 5
    
    for sc in scenarios:
        req = DecisionRequest(
            decision=sc["decision"],
            reasoning=sc["reasoning"],
            priorities=sc.get("priorities", ""),
            constraints=sc.get("constraints", ""),
            options_considered=sc.get("options_considered", [])
        )
        res = analyze_with_heuristics(req)
        assert res.decision_summary == sc["decision"]
        assert len(res.potential_blind_spots) > 0
        assert len(res.assumptions_to_examine) > 0
        assert len(res.conflicts_and_tensions) > 0
        assert len(res.reflective_questions) > 0
        assert "yours" in res.decision_ownership_statement.lower()
