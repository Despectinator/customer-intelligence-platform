import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID

from app.database.database import Base


class SegmentHistory(Base):
    __tablename__ = "segment_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    old_segment = Column(String, nullable=True)
    new_segment = Column(String, nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
