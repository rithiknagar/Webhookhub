from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from datetime import datetime

from webhookhub.db.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(320), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    api_keys = relationship("APIKeyModel", back_populates="user", cascade="all, delete-orphan")

    webhook_endpoints = relationship( "WebhookEndpointModel", back_populates="user", cascade="all, delete-orphan" )

    events = relationship( "EventModel", back_populates="user", cascade="all, delete-orphan")