import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from backend.db.database import Base

class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    user_query = Column(Text, nullable=False)
    groq_answer = Column(Text, nullable=True)
    model_used = Column(String, nullable=True)
    token_usage = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
