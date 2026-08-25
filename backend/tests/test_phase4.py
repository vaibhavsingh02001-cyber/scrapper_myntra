import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from backend.main import app
from backend.db.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Setup in-memory test database with StaticPool so all connections share the same memory DB
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_health_endpoint():
    with patch("backend.services.groq_service.GroqService.health_check", return_value=True):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["database"] == "connected"

def test_scrape_endpoint_submits_job():
    payload = {
        "url": "https://quotes.toscrape.com",
        "prompt": "Extract all quotes and authors",
        "mode": "auto"
    }

    with patch("backend.routers.scrape.run_scrape_pipeline", new_callable=AsyncMock):
        response = client.post("/scrape/", json=payload)
        assert response.status_code == 202
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "queued"

        # Verify job list returns the created job
        job_id = data["job_id"]
        job_response = client.get(f"/jobs/{job_id}")
        assert job_response.status_code == 200
        job_data = job_response.json()
        assert job_data["url"] == "https://quotes.toscrape.com/"
        assert job_data["status"] == "queued"

def test_query_and_export_flow():
    # Submit job
    payload = {"url": "https://example.com", "prompt": "Extract title"}

    with patch("backend.routers.scrape.run_scrape_pipeline", new_callable=AsyncMock):
        post_resp = client.post("/scrape/", json=payload)
        job_id = post_resp.json()["job_id"]

    # Manually mark completed & add result data
    from backend.services import job_service
    db = TestingSession()
    job_service.save_result(db, job_id, [{"title": "Example Domain", "price": "$0"}], mode_used="beautifulsoup")
    job_service.update_job_status(db, job_id, "completed")
    db.close()

    # Test Query endpoint
    mock_query_res = ({"answer": "The title is Example Domain", "relevant_records": None}, 100)
    with patch("backend.services.groq_service.GroqService.query", return_value=mock_query_res):
        q_resp = client.post("/query/", json={"job_id": job_id, "query": "What is the title?"})
        assert q_resp.status_code == 200
        assert "Example Domain" in q_resp.json()["answer"]

    # Test Export JSON endpoint
    exp_json = client.get(f"/export/{job_id}?format=json")
    assert exp_json.status_code == 200
    assert "Example Domain" in exp_json.text

    # Test Export CSV endpoint
    exp_csv = client.get(f"/export/{job_id}?format=csv")
    assert exp_csv.status_code == 200
    assert "Example Domain" in exp_csv.text

    # Test Delete job
    del_resp = client.delete(f"/jobs/{job_id}")
    assert del_resp.status_code == 200

    # Confirm 404 after deletion
    get_del = client.get(f"/jobs/{job_id}")
    assert get_del.status_code == 404
