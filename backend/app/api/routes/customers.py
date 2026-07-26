"""
Customer CRUD endpoints, scoped under a project:
GET/POST /projects/{project_id}/customers, GET/PUT/DELETE /customers/{id}.
See docs/api/API-Design.md. To be implemented in Module 2.
"""

# Endpoints go here. Once implemented, wire this into routes/__init__.py:
#   from app.api.routes import customers
#   api_router.include_router(customers.router)

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.core.security import CurrentUser
from app.schemas import (
    CustomerCreate,
    CustomerUpdate,
    CustomerOut,
)
from app.services import (
    customer_service,
    project_service,
)

router = APIRouter(
    prefix="/projects/{project_id}/customers",
    tags=["Customers"],
)


@router.get("", response_model=list[CustomerOut])
def list_customers(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    # Verify project ownership
    project_service.get_owned_project(
        db,
        project_id,
        current_user.id,
    )

    return customer_service.list_customers(
        db,
        project_id,
    )


@router.post(
    "",
    response_model=CustomerOut,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    project_id: uuid.UUID,
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    # Verify project ownership
    project_service.get_owned_project(
        db,
        project_id,
        current_user.id,
    )

    return customer_service.create_customer(
        db,
        project_id,
        payload,
    )


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(
    project_id: uuid.UUID,
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    project_service.get_owned_project(
        db,
        project_id,
        current_user.id,
    )

    return customer_service.get_customer(
        db,
        customer_id,
        project_id,
    )


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(
    project_id: uuid.UUID,
    customer_id: uuid.UUID,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    project_service.get_owned_project(
        db,
        project_id,
        current_user.id,
    )

    return customer_service.update_customer(
        db,
        customer_id,
        project_id,
        payload,
    )


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_customer(
    project_id: uuid.UUID,
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    project_service.get_owned_project(
        db,
        project_id,
        current_user.id,
    )

    customer_service.delete_customer(
        db,
        customer_id,
        project_id,
    )

    return None