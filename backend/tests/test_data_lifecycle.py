import uuid
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.database.models import Customer, Project, Transaction
from app.schemas import CustomerCreate, ProjectCreate
from app.services import customer_service, project_service


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


def test_customer_deletion_removes_transactions(db):
    project = Project(user_id=uuid.uuid4(), name="Store")
    db.add(project)
    db.commit()
    customer = customer_service.create_customer(
        db,
        project.id,
        CustomerCreate(first_name="Test", last_name="Customer", email="test@example.com"),
    )
    db.add(Transaction(customer_id=customer.id, order_date=date.today(), order_amount="25.00"))
    db.commit()

    customer_service.delete_customer(db, customer.id, project.id)

    assert db.query(Customer).filter(Customer.id == customer.id).first() is None
    assert db.query(Transaction).filter(Transaction.customer_id == customer.id).count() == 0


def test_project_deletion_removes_customers_and_transactions(db):
    user_id = uuid.uuid4()
    project = project_service.create_project(db, user_id, ProjectCreate(name="Store"))
    customer = Customer(
        project_id=project.id,
        first_name="Test",
        last_name="Customer",
        email="test@example.com",
    )
    db.add(customer)
    db.commit()
    db.add(Transaction(customer_id=customer.id, order_date=date.today(), order_amount="25.00"))
    db.commit()

    project_service.delete_project(db, project.id, user_id)

    assert db.query(Project).filter(Project.id == project.id).first() is None
    assert db.query(Customer).filter(Customer.id == customer.id).first() is None
    assert db.query(Transaction).filter(Transaction.customer_id == customer.id).count() == 0
