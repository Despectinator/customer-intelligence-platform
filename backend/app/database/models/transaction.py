import uuid
from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    order_date = Column(Date, nullable=False)
    order_amount = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Customer", back_populates="transactions")
