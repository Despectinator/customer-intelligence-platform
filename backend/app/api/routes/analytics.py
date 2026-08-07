"""
Segment and dashboard endpoints: /projects/{id}/segments,
/projects/{id}/segments/summary, /customers/{id}/segment,
/projects/{id}/segments/recompute, /projects/{id}/dashboard/overview,
/projects/{id}/dashboard/migrations. See docs/api/API-Design.md.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.core.security import CurrentUser
from app.database.models import Customer, Project, Segment
from app.schemas.segment import (
    SegmentOut,
    SegmentSummary,
    DashboardOverview,
    SegmentHistoryOut,
    RevenueByDate,
)
from app.services import project_service, analytics_service
from app.analytics.dashboard import get_dashboard_overview
from app.analytics.revenue import revenue_by_segment, revenue_by_date
from app.analytics.insights import get_recommendation

router = APIRouter(tags=["Analytics"])


def _segment_to_out(segment: Segment) -> SegmentOut:
    return SegmentOut(
        customer_id=segment.customer_id,
        cluster_number=segment.cluster_number,
        segment_name=segment.segment_name,
        recommendation=get_recommendation(segment.segment_name),
        generated_at=segment.generated_at,
    )


def _verify_customer_ownership(db: Session, customer_id: uuid.UUID, user_id: uuid.UUID) -> None:
    # Same pattern as transactions.py: a customer's ownership is checked
    # by joining through Project, since there's no direct user_id on
    # Customer, and this endpoint isn't nested under /projects/{id}.
    owned = (
        db.query(Customer)
        .join(Project, Customer.project_id == Project.id)
        .filter(Customer.id == customer_id, Project.user_id == user_id)
        .first()
    )
    if not owned:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")


@router.get("/projects/{project_id}/segments", response_model=list[SegmentOut])
def list_segments(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    project_service.get_owned_project(db, project_id, current_user.id)
    segments = analytics_service.list_project_segments(db, project_id)
    return [_segment_to_out(s) for s in segments]


@router.get("/projects/{project_id}/segments/summary", response_model=list[SegmentSummary])
def segments_summary(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    project_service.get_owned_project(db, project_id, current_user.id)
    return revenue_by_segment(db, project_id)


@router.post("/projects/{project_id}/segments/recompute", response_model=list[SegmentOut])
def recompute_segments(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Manually triggers a full re-cluster for the project — e.g. after a
    bulk CSV import, where recomputing after every single inserted row
    would be wasteful (see docs/architecture/CSV-Upload-Flow.md).
    """
    project_service.get_owned_project(db, project_id, current_user.id)
    analytics_service.recompute_project_segments(db, project_id)
    segments = analytics_service.list_project_segments(db, project_id)
    return [_segment_to_out(s) for s in segments]


@router.get("/customers/{customer_id}/segment", response_model=SegmentOut)
def get_customer_segment(
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    _verify_customer_ownership(db, customer_id, current_user.id)
    segment = analytics_service.get_customer_segment(db, customer_id)
    if not segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No segment computed yet for this customer",
        )
    return _segment_to_out(segment)


@router.get("/projects/{project_id}/dashboard/overview", response_model=DashboardOverview)
def dashboard_overview(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    project_service.get_owned_project(db, project_id, current_user.id)
    return get_dashboard_overview(db, project_id)


@router.get(
    "/projects/{project_id}/dashboard/revenue",
    response_model=list[RevenueByDate],
)
def dashboard_revenue(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    project_service.get_owned_project(db, project_id, current_user.id)
    return revenue_by_date(db, project_id)


@router.get("/projects/{project_id}/dashboard/migrations", response_model=list[SegmentHistoryOut])
def dashboard_migrations(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    project_service.get_owned_project(db, project_id, current_user.id)
    return analytics_service.list_recent_migrations(db, project_id)
