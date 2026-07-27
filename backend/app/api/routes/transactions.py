import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
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


@router.get(
    "",
    response_model=list[TransactionOut],
)
def list_transactions(
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
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
    current_user=Depends(get_current_user),
):
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
    current_user=Depends(get_current_user),
):
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
    current_user=Depends(get_current_user),
):
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
    current_user=Depends(get_current_user),
):
    transaction_service.delete_transaction(
        db,
        transaction_id,
        customer_id,
    )