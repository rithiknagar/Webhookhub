from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from webhookhub.db.models.delivery import DeliveryModel
from webhookhub.db.models.webhook_endpoint import WebhookEndpointModel
from webhookhub.db.models.webhook_endpoint import WebhookSubscriptionModel
from webhookhub.db.models.events import EventModel


async def route_event(session: AsyncSession, event: EventModel) -> list[DeliveryModel]:
    """
    Find all active webhook endpoints subscribed to this event type
    and create one delivery for each matching endpoint.
    """

    result = await session.execute(
        select(WebhookEndpointModel)
        .join(
            WebhookSubscriptionModel,
            WebhookSubscriptionModel.endpoint_id
            == WebhookEndpointModel.id,
        )
        .where(
            WebhookEndpointModel.user_id == event.user_id,
            WebhookEndpointModel.is_active.is_(True),
            WebhookSubscriptionModel.event_type == event.event_type,
        )
    )

    endpoints = result.scalars().all()

    deliveries = []

    for endpoint in endpoints:
        delivery = DeliveryModel(
            event_id=event.id,
            endpoint_id=endpoint.id,
            status="pending",
        )

        session.add(delivery)
        deliveries.append(delivery)

    if deliveries:
        await session.flush()

    return deliveries