"""
CSV bulk import endpoint: POST /projects/{project_id}/transactions/upload-csv.
See docs/architecture/CSV-Upload-Flow.md for the full validation and
recompute design.

Note on response shape: docs/api/API-Design.md's original sketch wrapped
responses as {"success": true, "data": {...}} (see app/schemas/common.py),
but every other endpoint in this API (Projects, Customers, Transactions,
Analytics) returns the resource directly with no envelope, relying on
HTTP status codes for success/failure. This endpoint follows that same
established convention for consistency, rather than being the one
endpoint that does it differently.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.core.security import CurrentUser
from app.schemas.upload import UploadResult
from app.services import project_service, upload_service

router = APIRouter(tags=["Upload"])

MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


@router.post(
    "/projects/{project_id}/transactions/upload-csv",
    response_model=UploadResult,
)
async def upload_transactions_csv(
    project_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    project_service.get_owned_project(db, project_id, current_user.id)

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be a .csv file")

    raw_bytes = await file.read()
    if len(raw_bytes) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File exceeds 5MB limit")

    try:
        file_contents = raw_bytes.decode("utf-8-sig")  # -sig strips a BOM if Excel added one
    except UnicodeDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be UTF-8 encoded")

    return upload_service.process_csv_upload(db, project_id, file_contents)
