from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from webhookhub.db.models.delivery import DeliveryModel
from webhookhub.db.models.events import EventModel
from webhookhub.db.models.webhook_endpoint import WebhookEndpointModel
from webhookhub.db.models.delivery_attempt_model import DeliveryAttemptModel




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


async def replay_delivery( db: AsyncSession, delivery_id: UUID, user_id: UUID) -> DeliveryModel | None:

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
        .with_for_update()
    )

    delivery = result.scalar_one_or_none()

    if delivery is None:
        return None

    if delivery.status not in {"failed", "exhausted"}:
        raise ValueError(
            "Only failed or exhausted deliveries can be replayed"
        )

    delivery.status = "pending"
    delivery.attempt_count = 0
    delivery.next_attempt_at = None
    delivery.last_attempt_at = None
    delivery.response_status = None
    delivery.last_error = None

    await db.commit()
    await db.refresh(delivery)

    return delivery


async def list_delivery_attempts(
    db: AsyncSession,
    delivery_id: UUID,
    user_id: UUID,
):
    ownership_query = (
        select(DeliveryModel.id)
        .join(
            EventModel,
            DeliveryModel.event_id == EventModel.id,
        )
        .join(
            WebhookEndpointModel,
            DeliveryModel.endpoint_id
            == WebhookEndpointModel.id,
        )
        .where(
            DeliveryModel.id == delivery_id,
            EventModel.user_id == user_id,
            WebhookEndpointModel.user_id == user_id,
        )
    )

    ownership_result = await db.execute(
        ownership_query
    )

    delivery_exists = (
        ownership_result.scalar_one_or_none()
    )

    if delivery_exists is None:
        return None, 0

    count_query = select(
        func.count(DeliveryAttemptModel.id)
    ).where(
        DeliveryAttemptModel.delivery_id == delivery_id
    )

    count_result = await db.execute(count_query)

    total = count_result.scalar_one()

    result = await db.execute(
        select(DeliveryAttemptModel)
        .where(
            DeliveryAttemptModel.delivery_id
            == delivery_id
        )
        .order_by(
            DeliveryAttemptModel.attempt_number.asc()
        )
    )

    attempts = result.scalars().all()

    return attempts, total



async def get_next_attempt_number(db: AsyncSession,delivery_id: UUID) -> int:

    result = await db.execute(
        select(func.max(DeliveryAttemptModel.attempt_number))
        .where(
            DeliveryAttemptModel.delivery_id == delivery_id
        )
    )

    max_attempt_number = result.scalar_one_or_none()

    if max_attempt_number is None:
        return 1

    return max_attempt_number + 1