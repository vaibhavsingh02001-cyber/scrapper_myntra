import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Float, DateTime
from backend.db.database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    platform = Column(String, nullable=False)       # google_play | app_store | reddit
    app_id = Column(String, nullable=True)          # com.myntra.android | myntra | ajio
    app_name = Column(String, nullable=True)        # Myntra | AJIO
    review_id = Column(String, nullable=True)       # Platform native review ID
    review_text = Column(Text, nullable=False)
    rating = Column(Float, nullable=True)           # 1.0–5.0 for stores; null for reddit
    author = Column(String, nullable=True)
    review_date = Column(DateTime, nullable=True)
    language = Column(String, default="en")
    content_hash = Column(String, nullable=True)    # SHA-256 for deduplication
    is_filtered_out = Column(String, default="no")  # "no" | reason string
    created_at = Column(DateTime, default=datetime.utcnow)
