"""
CSV bulk import endpoint: POST /projects/{project_id}/transactions/upload-csv.
See docs/architecture/CSV-Upload-Flow.md for the full validation and
recompute design. To be implemented in Module 2.
"""
from fastapi import APIRouter

router = APIRouter(tags=["Upload"])

# Endpoint goes here. Once implemented, wire this into routes/__init__.py.
