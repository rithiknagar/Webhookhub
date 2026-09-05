from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class WebhookEndpointCreateSchema(BaseModel):
    name: str
    url: HttpUrl

class WebhookEndpointResponseSchema(BaseModel):
    id: UUID
    name: str
    url: str
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }

class WebhookEndpointCreateResponseSchema(BaseModel):
    id: UUID
    name: str
    url: str
    secret:str
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }

class WebhookSubscriptionCreateSchema(BaseModel):
    event_type: str

class WebhookSubscriptionResponseSchema(BaseModel):
    id: UUID
    endpoint_id: UUID
    event_type: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }