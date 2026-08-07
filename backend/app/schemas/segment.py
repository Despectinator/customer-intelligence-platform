"""
Pydantic schemas for Segment responses (read-only from the API's
perspective — segments are only ever written by the ML recompute flow,
never directly by a client).
"""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SegmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_id: uuid.UUID
    cluster_number: Optional[int] = None
    segment_name: Optional[str] = None
    recommendation: str
    generated_at: Optional[datetime] = None


class SegmentSummary(BaseModel):
    segment_name: str
    customer_count: int
    revenue_total: float
    revenue_percentage: float


class DashboardOverview(BaseModel):
    total_customers: int
    total_revenue: float
    segment_breakdown: list[SegmentSummary]


class RevenueByDate(BaseModel):
    date: str
    revenue: float


class SegmentHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_id: uuid.UUID
    old_segment: Optional[str] = None
    new_segment: str
    changed_at: datetime
