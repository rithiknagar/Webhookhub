from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DeliveryResponseSchema(BaseModel):
    id: UUID
    event_id: UUID
    endpoint_id: UUID

    status: str

    attempt_count: int

    next_attempt_at: datetime | None
    last_attempt_at: datetime | None

    response_status: int | None
    last_error: str | None

    created_at: datetime

    model_config = {
        "from_attributes": True,
    }

class DeliveryListResponseSchema(BaseModel):
    items: list[DeliveryResponseSchema]
    total: int
    page: int
    page_size: int