import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, CurrentUser
from app.database.database import get_db
from app.database.models import Customer, Project
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionOut,
)
from app.services import transaction_service

router = APIRouter(
    prefix="/customers/{customer_id}/transactions",
    tags=["Transactions"],
)


def _verify_customer_ownership(
    db: Session,
    customer_id: uuid.UUID,
    user_id: uuid.UUID,
) -> None:
    """
    A transaction is scoped to a customer, which belongs to a project,
    which belongs to a user. There's no project_id in this router's URL,
    so ownership has to be checked by joining Customer -> Project and
    confirming the project's user_id matches the caller. Raises 404
    (not 403) so an attacker probing customer_ids they don't own can't
    distinguish "doesn't exist" from "exists but isn't yours."
    """
    owned = (
        db.query(Customer)
        .join(Project, Customer.project_id == Project.id)
        .filter(Customer.id == customer_id, Project.user_id == user_id)
        .first()
    )
    if not owned:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")


@router.get(
    "",
    response_model=list[TransactionOut],
)
def list_transactions(
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    _verify_customer_ownership(db, customer_id, current_user.id)
    return transaction_service.list_transactions(
        db,
        customer_id,
    )


@router.post(
    "",
    response_model=TransactionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    customer_id: uuid.UUID,
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    _verify_customer_ownership(db, customer_id, current_user.id)
    return transaction_service.create_transaction(
        db,
        customer_id,
        payload,
    )


@router.get(
    "/{transaction_id}",
    response_model=TransactionOut,
)
def get_transaction(
    customer_id: uuid.UUID,
    transaction_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    _verify_customer_ownership(db, customer_id, current_user.id)
    return transaction_service.get_transaction(
        db,
        transaction_id,
        customer_id,
    )


@router.put(
    "/{transaction_id}",
    response_model=TransactionOut,
)
def update_transaction(
    customer_id: uuid.UUID,
    transaction_id: uuid.UUID,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    _verify_customer_ownership(db, customer_id, current_user.id)
    return transaction_service.update_transaction(
        db,
        transaction_id,
        customer_id,
        payload,
    )


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_transaction(
    customer_id: uuid.UUID,
    transaction_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    _verify_customer_ownership(db, customer_id, current_user.id)
    transaction_service.delete_transaction(
        db,
        transaction_id,
        customer_id,
    )
