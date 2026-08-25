import io
import csv
import json
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.services import job_service

router = APIRouter()

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flattens nested dictionaries for CSV export using dot notation."""
    items: List[tuple] = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            items.append((new_key, json.dumps(v, default=str)))
        else:
            items.append((new_key, v))
    return dict(items)

@router.get("/{job_id}")
async def export_job_results(
    job_id: str,
    format: str = Query("json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db)
):

    """Downloads extracted dataset for job_id in JSON or CSV format."""
    data = job_service.get_result_data(db, job_id)

    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No result data available for this job."
        )

    if format == "csv":
        output = io.StringIO()

        # Format records into list of flattened dicts
        records: List[Dict[str, Any]] = []
        if isinstance(data, list):
            records = [flatten_dict(item) if isinstance(item, dict) else {"value": item} for item in data]
        elif isinstance(data, dict):
            records = [flatten_dict(data)]
        else:
            records = [{"value": data}]

        fieldnames = list(dict.fromkeys([key for rec in records for key in rec.keys()])) if records else ["value"]

        writer = csv.DictWriter(output, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(records)

        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=job_{job_id}.csv"}
        )

    # JSON export
    json_bytes = json.dumps(data, indent=2, default=str).encode("utf-8")
    return StreamingResponse(
        io.BytesIO(json_bytes),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=job_{job_id}.json"}
    )
