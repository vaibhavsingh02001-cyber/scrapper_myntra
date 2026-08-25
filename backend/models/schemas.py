from pydantic import BaseModel, HttpUrl, field_validator, Field
from typing import Optional, Any, List, Dict
from datetime import datetime

class ScrapeRequest(BaseModel):
    url: HttpUrl
    prompt: str = Field(..., min_length=3, max_length=1000, description="Natural language extraction prompt")
    mode: str = Field("auto", pattern="^(auto|static|dynamic)$")

    @field_validator("url")
    @classmethod
    def validate_url_scheme_and_host(cls, v: HttpUrl) -> HttpUrl:
        scheme = v.scheme.lower()
        if scheme not in ["http", "https"]:
            raise ValueError("Only http and https URL schemes are allowed.")
        host = v.host.lower() if v.host else ""
        if host in ["localhost", "127.0.0.1", "::1"] or host.startswith("192.168.") or host.startswith("10."):
            raise ValueError("Scraping local or private network addresses is forbidden.")
        return v

class JobResponse(BaseModel):
    job_id: str
    status: str
    created_at: datetime

class ExportUrls(BaseModel):
    json_url: str
    csv_url: str


class JobDetailResponse(BaseModel):
    job_id: str
    status: str
    url: str
    prompt: str
    mode: str
    scrape_mode_used: Optional[str] = None
    groq_model_used: Optional[str] = None
    token_usage: Optional[int] = 0
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    record_count: Optional[int] = 0
    error_message: Optional[str] = None
    export_urls: Optional[ExportUrls] = None

class QueryRequest(BaseModel):
    job_id: str
    query: str = Field(..., min_length=1, max_length=1000)

class QueryResponse(BaseModel):
    answer: str
    relevant_records: Optional[List[Dict[str, Any]]] = None
