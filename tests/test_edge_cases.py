"""
Edge case and resilience testing for 'The Blind Spot'.
Covers all criteria from Section 13:
- Ambiguous input
- Missing context
- Long input
- API failure & network fallback
- Adversarial 'decide for me' enforcement
"""
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.app import app
from backend.models import DecisionRequest
from backend.gemini_service import analyze_decision_reasoning

client = TestClient(app)


def test_missing_optional_context():
    """Test decision analysis when all optional context fields are absent."""
    payload = {
        "decision": "Should I accept the offer?",
        "reasoning": "The offer has a high pay and good commute time.",
        "priorities": "",
        "constraints": "",
        "options_considered": []
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["potential_blind_spots"]) > 0
    assert len(data["reflective_questions"]) > 0


def test_ambiguous_decision_input():
    """Test handling of ambiguous or broad decision inputs."""
    req = DecisionRequest(
        decision="Should I make a big life change?",
        reasoning="I feel stuck in my current routine and want to try something completely new."
    )
    res = analyze_decision_reasoning(req)
    assert res.decision_summary == req.decision
    assert len(res.reflective_questions) >= 2
    assert "yours" in res.decision_ownership_statement.lower()


def test_long_valid_input():
    """Test processing of large valid decision and reasoning payloads."""
    long_reasoning = (
        "I have been contemplating this transition for several months. " * 30
    )
    payload = {
        "decision": "Should I pivot our entire company strategy to open source infrastructure?",
        "reasoning": long_reasoning[:3500],
        "priorities": "Sustainability, long-term developer adoption, and enterprise contracts.",
        "constraints": "12 months runway and 4 core engineers."
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["potential_blind_spots"]) > 0


def test_api_failure_fallback_resilience():
    """
    Test that when Google Gemini API throws an exception (network failure / quota error),
    the system seamlessly falls back to the deterministic heuristic engine without crashing.
    """
    req = DecisionRequest(
        decision="Should I accept the software internship?",
        reasoning="The stipend is very good (40k/month) and close to my home."
    )
    
    with patch("backend.gemini_service.get_gemini_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("API Quota Exceeded or Network Timeout")
        mock_get_client.return_value = mock_client
        
        # Analyze should not raise Exception, but gracefully fall back
        result = analyze_decision_reasoning(req)
        assert result is not None
        assert "stipend" in result.decision_summary.lower() or "internship" in result.decision_summary.lower()
        assert len(result.potential_blind_spots) > 0
        assert result.execution_mode == "heuristic_engine"


def test_no_decision_made_adversarial_queries():
    """
    Test multiple adversarial prompts attempting to force the AI to make the decision.
    Verify that in every case, the system refuses to decide.
    """
    queries = [
        ("Which one should I choose?", "Tell me which one is objectively better: Option A or Option B."),
        ("Make this decision for me", "I cannot decide myself. Give me the final answer now."),
        ("Accept or Reject?", "Should I take this internship yes or no?")
    ]
    for dec, rsn in queries:
        req = DecisionRequest(decision=dec, reasoning=rsn)
        result = analyze_decision_reasoning(req)
        statement = result.decision_ownership_statement.lower()
        assert "not" in statement or "solely" in statement or "yours" in statement
        forbidden = ["i recommend you accept", "you should choose option a", "my verdict is", "the correct choice is"]
        for f in forbidden:
            assert f not in statement


def test_meaningless_input_rejected_before_gemini_call():
    """Server-side validation must reject meaningless text before analysis is invoked."""
    invalid_payloads = [
        {"decision": "123456", "reasoning": "1234567890"},
        {"decision": "!!!???!!!", "reasoning": "!!!???!!!!!!!"},
        {"decision": "aaaaaa", "reasoning": "bbbbbbbbbb"},
    ]

    with patch("backend.app.analyze_decision_reasoning") as mock_analyze:
        for payload in invalid_payloads:
            response = client.post("/api/analyze", json=payload)
            assert response.status_code == 400

        mock_analyze.assert_not_called()


def test_mixed_numeric_text_input_is_accepted():
    """Legitimate numeric/text combinations must remain usable."""
    payload = {
        "decision": "Should I accept the 6-month internship?",
        "reasoning": "The ₹15,000 stipend and 3 days/week schedule are attractive, but I need to check my 85% attendance requirement.",
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
