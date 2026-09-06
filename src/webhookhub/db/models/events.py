from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint

from webhookhub.db.base import Base


class EventModel(Base):
    __tablename__ = "events"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    event_id = Column(String(255), nullable=False)
    event_type = Column(String(255), nullable=False)
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint( "user_id", "event_id", name="uq_event_user_event_id"),)

    user = relationship("UserModel", back_populates="events")

    deliveries = relationship("DeliveryModel",back_populates="event",cascade="all, delete-orphan")