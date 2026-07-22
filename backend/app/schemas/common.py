"""
Shared response envelope schemas, matching the format documented in
docs/api/API-Design.md:

  { "success": true, "data": {...} }
  { "success": false, "message": "..." }
"""
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
