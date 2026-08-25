import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_insights_status_endpoint():
    response = client.get("/insights/status")
    assert response.status_code == 200
    data = response.json()
    assert "themes_summary_exists" in data

def test_insights_list_themes():
    response = client.get("/insights/themes/list")
    assert response.status_code == 200
    data = response.json()
    assert "themes" in data

def test_insights_quotes_endpoint():
    response = client.get("/insights/quotes?theme=all&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "quotes" in data

def test_research_questions_endpoint():
    response = client.get("/research/questions")
    assert response.status_code == 200
    data = response.json()
    assert "questions" in data or "answers" in data

def test_opportunity_map_endpoint():
    response = client.get("/report/opportunity-map")
    assert response.status_code == 200
    data = response.json()
    assert "opportunity_map" in data
