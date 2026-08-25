import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from backend.db.database import Base

class Result(Base):
    __tablename__ = "results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    data = Column(Text, nullable=True)                  # Stored as JSON string
    raw_html_path = Column(Text, nullable=True)
    record_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
