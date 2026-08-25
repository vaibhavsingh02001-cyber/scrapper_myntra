import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime
from backend.db.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    url = Column(Text, nullable=False)
    prompt = Column(Text, nullable=False)
    mode = Column(String, default="auto")                # auto | static | dynamic
    status = Column(String, default="queued")            # queued | running | completed | failed | blocked
    error_message = Column(Text, nullable=True)
    scrape_mode_used = Column(String, nullable=True)     # beautifulsoup | playwright
    groq_model_used = Column(String, nullable=True)
    token_usage = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
