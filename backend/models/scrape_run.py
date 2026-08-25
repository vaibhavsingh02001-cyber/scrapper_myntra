import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from backend.db.database import Base

class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    platform = Column(String, nullable=False)           # google_play | app_store | reddit | all
    app_name = Column(String, nullable=True)            # Myntra | AJIO | all
    status = Column(String, default="running")          # running | completed | failed
    reviews_collected = Column(Integer, default=0)
    reviews_filtered = Column(Integer, default=0)
    reviews_stored = Column(Integer, default=0)
    error_message = Column(String, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
