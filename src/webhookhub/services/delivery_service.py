from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from webhookhub.db.models.delivery import DeliveryModel
from webhookhub.db.models.events import EventModel
from webhookhub.db.models.webhook_endpoint import WebhookEndpointModel


async def get_delivery(db: AsyncSession,delivery_id: UUID,user_id: UUID) -> DeliveryModel | None:

    result = await db.execute(
        select(DeliveryModel)
        .join(
            EventModel,
            DeliveryModel.event_id == EventModel.id,
        )
        .join(
            WebhookEndpointModel,
            DeliveryModel.endpoint_id == WebhookEndpointModel.id,
        )
        .where(
            DeliveryModel.id == delivery_id,
            EventModel.user_id == user_id,
            WebhookEndpointModel.user_id == user_id,
        )
    )
    delivery=result.scalar_one_or_none()

    return delivery



async def list_deliveries( db: AsyncSession, user_id: UUID,status_filter: str | None = None,event_id: UUID | None = None,
            endpoint_id: UUID | None = None, page: int = 1, page_size: int = 10):
    query = (
        select(DeliveryModel)
        .join(
            EventModel,
            DeliveryModel.event_id == EventModel.id,
        )
        .join(
            WebhookEndpointModel,
            DeliveryModel.endpoint_id == WebhookEndpointModel.id,
        )
        .where(
            EventModel.user_id == user_id,
            WebhookEndpointModel.user_id == user_id,
        )
    )

    if status_filter is not None:
        query = query.where(
            DeliveryModel.status == status_filter
        )

    if event_id is not None:
        query = query.where(
            DeliveryModel.event_id == event_id
        )

    if endpoint_id is not None:
        query = query.where(
            DeliveryModel.endpoint_id == endpoint_id
        )

    count_query = select(
        func.count(DeliveryModel.id)).select_from( query.subquery())

    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    offset = (page - 1) * page_size

    query = (
        query
        .order_by(
            DeliveryModel.created_at.desc()
        )
        .offset(offset)
        .limit(page_size)
    )

    result = await db.execute(query)

    deliveries = result.scalars().all()

    return deliveries, total


