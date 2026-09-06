from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from webhookhub.db.models.events import EventModel
from webhookhub.services.routing_service import route_event
from webhookhub.worker.tasks import deliver_webhook


async def get_event_by_event_id(session: AsyncSession,user_id,event_id: str ) -> EventModel | None:

    result = await session.execute( select(EventModel)
        .where(
            EventModel.user_id == user_id,
            EventModel.event_id == event_id,
        )
    )
    event=result.scalar_one_or_none()

    return event


async def create_event( session: AsyncSession,user_id,event_id: str,event_type: str,payload: dict,) -> EventModel:

    event = EventModel(
        user_id=user_id,
        event_id=event_id,
        event_type=event_type,
        payload=payload,
    )

    session.add(event)

    await session.flush()

    deliveries= await route_event(
        session=session,
        event=event,
    )
    print("deliveries created ",len(deliveries))
    
    for delivery in deliveries:
    
            deliver_webhook.delay(
                delivery.id
            )

    await session.commit()

    await session.refresh(event)

    return event