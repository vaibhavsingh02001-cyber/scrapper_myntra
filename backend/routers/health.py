from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.db.database import get_db
from backend.services import GroqService

router = APIRouter()

@router.get("/")
async def check_health(db: Session = Depends(get_db)):
    """Health check endpoint checking DB connection and Groq LLM API connectivity."""
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    groq = GroqService()
    groq_ok = await groq.health_check()

    overall_status = "ok" if db_ok else "degraded"

    return {
        "status": overall_status,
        "groq_api": "reachable" if groq_ok else "standby",
        "database": "connected" if db_ok else "error"
    }
