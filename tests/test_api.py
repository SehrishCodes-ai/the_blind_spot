"""
API integration tests for FastAPI endpoints in 'The Blind Spot'.
"""
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


def test_health_endpoint():
    """Verify health check returns service metadata."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "The Blind Spot" in data["app_name"]
    assert "gemini_api_configured" in data


def test_list_scenarios():
    """Verify preloaded scenarios can be fetched."""
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3
    ids = [s["id"] for s in data]
    assert "internship-dilemma" in ids


def test_get_scenario_by_id():
    """Verify fetching single scenario."""
    response = client.get("/api/scenarios/internship-dilemma")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "internship-dilemma"
    assert "stipend" in data["reasoning"].lower()


def test_analyze_endpoint_valid():
    """Verify POST /api/analyze processes valid request correctly."""
    payload = {
        "decision": "Should I accept a 6-month software development internship?",
        "reasoning": "The stipend is 40k, office is near my home, and it adds industry experience.",
        "priorities": "Maintain top GPA and learn deep software engineering.",
        "constraints": "Mandatory college classes Monday to Friday."
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "decision_summary" in data
    assert len(data["understanding"]) > 0
    assert len(data["potential_blind_spots"]) > 0
    assert len(data["assumptions_to_examine"]) > 0
    assert len(data["conflicts_and_tensions"]) > 0
    assert len(data["reflective_questions"]) > 0
    assert "The AI companion provides analysis" in data["decision_ownership_statement"] or "solely" in data["decision_ownership_statement"]


def test_analyze_endpoint_empty_decision():
    """Verify empty decision is rejected."""
    payload = {
        "decision": "",
        "reasoning": "Valid reasoning length provided here."
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 422


def test_analyze_endpoint_short_reasoning():
    """Verify reasoning under 10 chars is rejected."""
    payload = {
        "decision": "Valid decision title?",
        "reasoning": "Too short"
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 422


def test_deep_dive_endpoint_valid():
    """Verify deep dive reflection returns mirror and follow up questions."""
    payload = {
        "decision": "Should I accept the internship?",
        "selected_question_or_assumption": "What if the stipend was zero?",
        "user_reflection": "If the stipend was zero I would definitely reject it because my primary goal is saving money."
    }
    response = client.post("/api/deep-dive", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == payload["selected_question_or_assumption"]
    assert len(data["probing_follow_up_questions"]) >= 2
    assert "reminder" in data


def test_deep_dive_empty_reflection():
    """Verify empty reflection is rejected with 400 Bad Request."""
    payload = {
        "decision": "Should I accept the internship?",
        "selected_question_or_assumption": "What if the stipend was zero?",
        "user_reflection": "   "
    }
    response = client.post("/api/deep-dive", json=payload)
    assert response.status_code == 400


def test_serve_frontend_index():
    """Verify GET / serves the frontend application."""
    response = client.get("/")
    assert response.status_code == 200
    assert "The Blind Spot" in response.text
    assert "AI Critical Thinking Companion" in response.text

