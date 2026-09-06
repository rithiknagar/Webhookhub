from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class EventCreateSchema(BaseModel):

    event_id: str = Field( min_length=1,max_length=255)
    event_type: str = Field( min_length=1, max_length=255,)
    payload: dict[str, Any]

class EventResponseSchema(BaseModel):
    
    id: UUID
    event_id: str
    event_type: str
    payload: dict[str, Any]
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }