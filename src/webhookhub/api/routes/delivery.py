from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from webhookhub.db.session import get_db_session
from webhookhub.schemas.delivery_schema import DeliveryResponseSchema
from webhookhub.services.delivery_service import get_delivery

from webhookhub.api.dependencies.auth import get_current_user
from fastapi import Query

from webhookhub.schemas.delivery_schema import  DeliveryListResponseSchema
from webhookhub.services.delivery_service import list_deliveries
from webhookhub.worker.tasks import deliver_webhook


router = APIRouter(prefix="/v1/deliveries",tags=["Deliveries"])


@router.get("/{delivery_id}",response_model=DeliveryResponseSchema,)
async def get_delivery_details(delivery_id: UUID,current_user=Depends(get_current_user),db: AsyncSession = Depends(get_db_session)):

    delivery = await get_delivery(
        db=db,
        delivery_id=delivery_id,
        user_id=current_user.id,
    )

    if delivery is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found",
        )

    return delivery


@router.get("", response_model=DeliveryListResponseSchema)
async def get_deliveries(
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    event_id: UUID | None = None,
    endpoint_id: UUID | None = None,
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    deliveries, total = await list_deliveries(
        db=db,
        user_id=current_user.id,
        status_filter=status_filter,
        event_id=event_id,
        endpoint_id=endpoint_id,
        page=page,
        page_size=page_size,
    )

    return {
        "items": deliveries,
        "total": total,
        "page": page,
        "page_size": page_size,
    }

