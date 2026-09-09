import uuid
from datetime import datetime

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from webhookhub.db.base import Base


class DeliveryAttemptModel(Base):
    __tablename__ = "delivery_attempts"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    delivery_id = Column(PGUUID(as_uuid=True), ForeignKey("deliveries.id"), nullable=False, index=True)
    attempt_number = Column(Integer, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    response_status = Column(Integer, nullable=True)
    error = Column(String(1000), nullable=True)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    delivery = relationship("DeliveryModel", back_populates="attempts")