from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from webhookhub.api.dependencies.auth import get_current_user
from webhookhub.db.models.user import UserModel
from webhookhub.db.session import get_db_session
from webhookhub.schemas.webhook import WebhookEndpointCreateSchema, WebhookEndpointResponseSchema,WebhookSubscriptionResponseSchema, WebhookSubscriptionCreateSchema, WebhookEndpointCreateResponseSchema
from webhookhub.services.webhook_endpoint_service import  create_webhook_endpoint, get_webhook_endpoint_for_user, create_subscription, list_webhook_endpoints, delete_subscription, list_subscriptions, rotate_endpoint_secret
from webhookhub.api.dependencies.rate_limit import event_rate_limit

router = APIRouter( prefix="/v1/webhook-endpoints",tags=["Webhook Endpoints"])



@router.get("", response_model=list[WebhookEndpointResponseSchema])
async def list_endpoints( current_user: UserModel = Depends( event_rate_limit), session: AsyncSession = Depends(get_db_session)):

    return await list_webhook_endpoints(
        session=session,
        user_id=current_user.id,
    )

@router.get("/{endpoint_id}/subscriptions", response_model=list[WebhookSubscriptionResponseSchema])
async def list_endpoints( endpoint_id:UUID, current_user: UserModel = Depends( get_current_user), session: AsyncSession = Depends(get_db_session)):

    return await list_subscriptions(
        session=session,
        endpoint_id=endpoint_id,
        user_id=current_user.id,
    )

@router.post( "", response_model=WebhookEndpointCreateResponseSchema, status_code=status.HTTP_201_CREATED)

async def create_endpoint( payload: WebhookEndpointCreateSchema,current_user: UserModel = Depends( get_current_user),
    session: AsyncSession = Depends(get_db_session) ):

    endpoint = await create_webhook_endpoint(
        session=session,
        user_id=current_user.id,
        name=payload.name,
        url=str(payload.url),
    )

    return endpoint

@router.post("/{endpoint_id}/subscriptions", response_model=WebhookSubscriptionResponseSchema,status_code=status.HTTP_201_CREATED)
async def create_endpoint_subscription( endpoint_id: UUID, payload: WebhookSubscriptionCreateSchema, 
            current_user: UserModel = Depends(get_current_user),session: AsyncSession = Depends(get_db_session)):
    
    endpoint = await get_webhook_endpoint_for_user(
        session=session,
        endpoint_id=endpoint_id,
        user_id=current_user.id,
    )

    if endpoint is None:
        raise HTTPException( status_code=status.HTTP_404_NOT_FOUND, detail="Webhook endpoint not found")

    try:
        subscription = await create_subscription(
            session=session,
            endpoint_id=endpoint.id,
            event_type=payload.event_type,
        )

    except ValueError as exc:
        raise HTTPException( status_code=status.HTTP_409_CONFLICT, detail=str(exc) )

    return subscription

@router.post("/{endpoint_id}/rotate-secret")
async def rotate_secret(endpoint_id: UUID, current_user=Depends(get_current_user),session: AsyncSession = Depends(get_db_session)):
    new_secret = await rotate_endpoint_secret(
        session=session,
        endpoint_id=endpoint_id,
        user_id=current_user.id,
    )

    if new_secret is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook endpoint not found",
        )

    return {
        "secret": new_secret,
    }

@router.delete("/subscriptions/{subscription_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_endpoint_subscription( subscription_id: UUID,current_user: UserModel = Depends(
        get_current_user), session: AsyncSession = Depends(get_db_session)):
    
    deleted = await delete_subscription(
        session=session,
        subscription_id=subscription_id,
        user_id=current_user.id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )