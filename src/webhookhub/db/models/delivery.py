import uuid

from datetime import datetime

from sqlalchemy import  Column, DateTime,ForeignKey,Integer,String,UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from webhookhub.db.base import Base


class DeliveryModel(Base):
    __tablename__ = "deliveries"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(PGUUID(as_uuid=True), ForeignKey("events.id"), nullable=False, index=True)
    endpoint_id = Column(PGUUID(as_uuid=True), ForeignKey("webhook_endpoints.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    attempt_count = Column(Integer, nullable=False, default=0)
    next_attempt_at = Column(DateTime(timezone=True), nullable=True, index=True)
    last_attempt_at = Column(DateTime(timezone=True), nullable=True)
    response_status = Column(Integer, nullable=True)
    last_error = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    event = relationship("EventModel", back_populates="deliveries")
    endpoint = relationship("WebhookEndpointModel", back_populates="deliveries")

    __table_args__ = (
        UniqueConstraint("event_id", "endpoint_id", name="uq_delivery_event_endpoint"),
    )