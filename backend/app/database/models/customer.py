import uuid

from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    DateTime,
    func,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.database import Base


class Customer(Base):
    __tablename__ = "customers"

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "email",
            name="uq_customer_project_email",
        ),
        Index("ix_customer_project_id", "project_id"),
        Index("ix_customer_email", "email"),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    first_name = Column(
        String(100),
        nullable=False,
    )

    last_name = Column(
        String(100),
        nullable=False,
    )

    email = Column(
        String(255),
        nullable=False,
    )

    phone = Column(
        String(30),
        nullable=True,
    )

    company = Column(
        String(255),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships

    project = relationship(
        "Project",
        back_populates="customers",
    )

    transactions = relationship(
        "Transaction",
        back_populates="customer",
        cascade="all, delete-orphan",
    )