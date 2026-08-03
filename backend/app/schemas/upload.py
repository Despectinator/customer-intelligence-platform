"""
Pydantic schemas for the CSV upload endpoint response.
See docs/architecture/CSV-Upload-Flow.md.
"""
from pydantic import BaseModel


class UploadRowError(BaseModel):
    row: int
    reason: str


class UploadResult(BaseModel):
    customers_created: int
    transactions_inserted: int
    rows_skipped: int
    errors: list[UploadRowError]
