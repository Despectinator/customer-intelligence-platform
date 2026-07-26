import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import Customer
from app.schemas import CustomerCreate, CustomerUpdate


def list_customers(
    db: Session,
    project_id: uuid.UUID,
) -> list[Customer]:
    return (
        db.query(Customer)
        .filter(Customer.project_id == project_id)
        .order_by(Customer.created_at.desc())
        .all()
    )


def create_customer(
    db: Session,
    project_id: uuid.UUID,
    payload: CustomerCreate,
) -> Customer:
    customer = Customer(
        project_id=project_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone=payload.phone,
        company=payload.company,
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


def get_customer(
    db: Session,
    customer_id: uuid.UUID,
    project_id: uuid.UUID,
) -> Customer:
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.project_id == project_id,
        )
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    return customer


def update_customer(
    db: Session,
    customer_id: uuid.UUID,
    project_id: uuid.UUID,
    payload: CustomerUpdate,
) -> Customer:
    customer = get_customer(
        db,
        customer_id,
        project_id,
    )

    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(customer, key, value)

    db.commit()
    db.refresh(customer)

    return customer


def delete_customer(
    db: Session,
    customer_id: uuid.UUID,
    project_id: uuid.UUID,
) -> None:
    customer = get_customer(
        db,
        customer_id,
        project_id,
    )

    db.delete(customer)
    db.commit()