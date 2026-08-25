import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.db.database import Base
from backend.models.job import Job
from backend.models.result import Result
from backend.models.query_history import QueryHistory
from backend.models.schemas import ScrapeRequest, JobDetailResponse

# Use an in-memory SQLite database for fast unit testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def setup_module():
    Base.metadata.create_all(bind=engine)

def teardown_module():
    Base.metadata.drop_all(bind=engine)

def test_create_and_read_job():
    db = TestingSessionLocal()
    new_job = Job(url="https://example.com", prompt="Extract titles", mode="auto")
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    fetched_job = db.query(Job).filter(Job.id == new_job.id).first()
    assert fetched_job is not None
    assert fetched_job.url == "https://example.com"
    assert fetched_job.status == "queued"
    db.close()

def test_create_result_linked_to_job():
    db = TestingSessionLocal()
    new_job = Job(url="https://example.com/products", prompt="Extract prices")
    db.add(new_job)
    db.commit()

    result_data = '[{"product": "Laptop", "price": "$999"}]'
    new_result = Result(job_id=new_job.id, data=result_data, record_count=1)
    db.add(new_result)
    db.commit()

    fetched_result = db.query(Result).filter(Result.job_id == new_job.id).first()
    assert fetched_result is not None
    assert fetched_result.record_count == 1
    assert "Laptop" in fetched_result.data
    db.close()

def test_create_query_history():
    db = TestingSessionLocal()
    new_job = Job(url="https://example.com/products", prompt="Extract prices")
    db.add(new_job)
    db.commit()

    history = QueryHistory(job_id=new_job.id, user_query="What is the price?", groq_answer="The price is $999.")
    db.add(history)
    db.commit()

    fetched_history = db.query(QueryHistory).filter(QueryHistory.job_id == new_job.id).first()
    assert fetched_history is not None
    assert fetched_history.groq_answer == "The price is $999."
    db.close()

def test_scrape_request_validation():
    valid_req = ScrapeRequest(url="https://quotes.toscrape.com", prompt="Extract quotes", mode="auto")
    assert str(valid_req.url) == "https://quotes.toscrape.com/"

    with pytest.raises(ValueError):
        # Invalid scheme (ftp) should fail validation
        ScrapeRequest(url="ftp://example.com", prompt="Extract quotes")

    with pytest.raises(ValueError):
        # Localhost IP should fail validation
        ScrapeRequest(url="http://127.0.0.1/admin", prompt="Extract quotes")
