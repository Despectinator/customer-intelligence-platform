import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID

from app.database.database import Base


class Segment(Base):
    __tablename__ = "segments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), unique=True, nullable=False)
    cluster_number = Column(Integer, nullable=True)
    segment_name = Column(String, nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
