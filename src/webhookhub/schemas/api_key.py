from datetime import datetime

from pydantic import BaseModel


class APIKeyCreateSchema(BaseModel):
    name: str


class APIKeyResponseSchema(BaseModel):
    id: str
    name: str
    key: str
    key_prefix: str
    created_at: datetime


class APIKeyListResponseSchema(BaseModel):
    id: str
    name: str
    key_prefix: str
    last_used_at: datetime | None
    expires_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime