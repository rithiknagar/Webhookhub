from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from webhookhub.api.dependencies.auth import get_current_user
from webhookhub.db.models.user import UserModel
from webhookhub.db.session import get_db_session
from webhookhub.schemas.event import EventCreateSchema, EventResponseSchema
from webhookhub.services.event_service import  create_event, get_event_by_event_id
from webhookhub.api.dependencies.rate_limit import event_rate_limit


router = APIRouter( prefix="/v1/events", tags=["Events"])

@router.post("", response_model=EventResponseSchema)
async def ingest_event( payload: EventCreateSchema, current_user: UserModel = Depends( event_rate_limit),session: AsyncSession = Depends(get_db_session),):

    existing_event = await get_event_by_event_id(session=session, user_id=current_user.id, event_id=payload.event_id)
    

    if existing_event:

        if (
            existing_event.event_type == payload.event_type
            and existing_event.payload == payload.payload
        ):
    
            return existing_event


        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Event ID already exists with different event data")
    

    event = await create_event(
        session=session,
        user_id=current_user.id,
        event_id=payload.event_id,
        event_type=payload.event_type,
        payload=payload.payload,
    )

    return event