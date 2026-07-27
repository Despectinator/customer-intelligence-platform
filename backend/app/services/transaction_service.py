import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import Transaction
from app.schemas import TransactionCreate, TransactionUpdate


def list_transactions(
    db: Session,
    customer_id: uuid.UUID,
) -> list[Transaction]:
    return (
        db.query(Transaction)
        .filter(Transaction.customer_id == customer_id)
        .order_by(Transaction.order_date.desc())
        .all()
    )


def create_transaction(
    db: Session,
    customer_id: uuid.UUID,
    payload: TransactionCreate,
) -> Transaction:
    transaction = Transaction(
        customer_id=customer_id,
        order_date=payload.order_date,
        order_amount=payload.order_amount,
        payment_method=payload.payment_method,
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    # TODO: Trigger analytics recomputation for this customer.

    return transaction


def get_transaction(
    db: Session,
    transaction_id: uuid.UUID,
    customer_id: uuid.UUID,
) -> Transaction:
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.customer_id == customer_id,
        )
        .first()
    )

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    return transaction


def update_transaction(
    db: Session,
    transaction_id: uuid.UUID,
    customer_id: uuid.UUID,
    payload: TransactionUpdate,
) -> Transaction:
    transaction = get_transaction(
        db,
        transaction_id,
        customer_id,
    )

    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(transaction, key, value)

    db.commit()
    db.refresh(transaction)

    # TODO: Trigger analytics recomputation for this customer.

    return transaction


def delete_transaction(
    db: Session,
    transaction_id: uuid.UUID,
    customer_id: uuid.UUID,
) -> None:
    transaction = get_transaction(
        db,
        transaction_id,
        customer_id,
    )

    db.delete(transaction)
    db.commit()

    # TODO: Trigger analytics recomputation for this customer.