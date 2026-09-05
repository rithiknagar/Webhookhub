from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy import select
from webhookhub.db.models.webhook_endpoint import  WebhookEndpointModel, WebhookSubscriptionModel
from sqlalchemy.exc import IntegrityError
import secrets

async def create_webhook_endpoint( session: AsyncSession, user_id, name: str,url: str,) -> WebhookEndpointModel:

    endpoint = WebhookEndpointModel(
        user_id=user_id,
        name=name,
        url=url,
        secret=secrets.token_urlsafe(32),
        is_active=True,
    )

    session.add(endpoint)

    await session.commit()
    await session.refresh(endpoint)

    return endpoint



async def create_subscription(session: AsyncSession, endpoint_id: UUID, event_type: str) -> WebhookSubscriptionModel:

    subscription = WebhookSubscriptionModel( endpoint_id=endpoint_id,event_type=event_type,)

    session.add(subscription)

    try:
        await session.commit()

    except IntegrityError:
        await session.rollback()

        raise ValueError(
            "This event type is already subscribed"
        )

    await session.refresh(subscription)

    return subscription

async def get_webhook_endpoint_for_user( session: AsyncSession, endpoint_id: UUID, user_id: UUID,) -> WebhookEndpointModel | None:

    result = await session.execute(
        select(WebhookEndpointModel)
        .where(
            WebhookEndpointModel.id == endpoint_id,
            WebhookEndpointModel.user_id == user_id,
        )
    )

    return result.scalar_one_or_none()

async def list_webhook_endpoints( session: AsyncSession, user_id: UUID) -> list[WebhookEndpointModel]:

    result = await session.execute(
        select(WebhookEndpointModel)
        .where(
            WebhookEndpointModel.user_id == user_id
        )
        .order_by(
            WebhookEndpointModel.created_at.desc()
        )
    )
    endpoints=result.scalars().all()

    return list(endpoints)

async def list_subscriptions(session: AsyncSession,endpoint_id: UUID,user_id: UUID,) -> list[WebhookSubscriptionModel]:

    result = await session.execute(
        select(WebhookSubscriptionModel)
        .join(
            WebhookEndpointModel,
            WebhookSubscriptionModel.endpoint_id
            == WebhookEndpointModel.id,
        )
        .where(
            WebhookSubscriptionModel.endpoint_id == endpoint_id,
            WebhookEndpointModel.user_id == user_id,
        )
        .order_by(
                    WebhookSubscriptionModel.created_at.desc()
        )
    )

    subscriptions = result.scalars().all()

    return list(subscriptions)

async def delete_subscription( session: AsyncSession, subscription_id: UUID, user_id: UUID,) -> bool:

    result = await session.execute(
        select(WebhookSubscriptionModel)
        .join(
            WebhookEndpointModel,
            WebhookSubscriptionModel.endpoint_id
            == WebhookEndpointModel.id,
        )
        .where(
            WebhookSubscriptionModel.id == subscription_id,
            WebhookEndpointModel.user_id == user_id,
        )
    )

    subscription = result.scalar_one_or_none()

    if subscription is None:
        return False

    await session.delete(subscription)
    await session.commit()

    return True