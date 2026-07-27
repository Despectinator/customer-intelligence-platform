import uuid

from sqlalchemy import (
    Column,
    String,
    Numeric,
    Date,
    DateTime,
    ForeignKey,
    func,
    Index,
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    __table_args__ = (
        Index("ix_transaction_customer_id", "customer_id"),
        Index("ix_transaction_order_date", "order_date"),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    customer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
    )

    order_date = Column(
        Date,
        nullable=False,
    )

    order_amount = Column(
        Numeric(12, 2),
        nullable=False,
    )

    payment_method = Column(
        String(50),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships

    customer = relationship(
        "Customer",
        back_populates="transactions",
    )