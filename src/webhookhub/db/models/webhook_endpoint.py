from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String,UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from webhookhub.db.base import Base


class WebhookEndpointModel(Base):
    __tablename__ = "webhook_endpoints"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(2048), nullable=False)
    secret = Column(String(255),nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    user = relationship("UserModel", back_populates="webhook_endpoints")

    subscriptions = relationship("WebhookSubscriptionModel", back_populates="endpoint", cascade="all, delete-orphan")

    deliveries = relationship( "DeliveryModel",back_populates="endpoint",cascade="all, delete-orphan")


class WebhookSubscriptionModel(Base):
    __tablename__ = "webhook_subscriptions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    endpoint_id = Column(PGUUID(as_uuid=True), ForeignKey("webhook_endpoints.id"), nullable=False, index=True)
    event_type = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    endpoint = relationship("WebhookEndpointModel", back_populates="subscriptions")

    __table_args__ = (
        UniqueConstraint("endpoint_id", "event_type", name="uq_webhook_endpoint_event_type"),
    )