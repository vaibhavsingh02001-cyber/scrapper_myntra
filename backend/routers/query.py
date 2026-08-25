from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.models.schemas import QueryRequest, QueryResponse
from backend.services import job_service, GroqService

router = APIRouter()

@router.post("/", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def query_scraped_data(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """Executes a natural language question against a job's extracted dataset."""
    result_data = job_service.get_result_data(db, request.job_id)

    groq = GroqService()
    response_dict, tokens_used = await groq.query(result_data, request.query)

    # Save query history record
    job_service.save_query_history(
        db=db,
        job_id=request.job_id,
        user_query=request.query,
        answer=response_dict["answer"],
        model_used=groq.query_model,
        token_usage=tokens_used
    )

    return QueryResponse(
        answer=response_dict["answer"],
        relevant_records=response_dict.get("relevant_records")
    )
