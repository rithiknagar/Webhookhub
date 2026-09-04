from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from webhookhub.api.dependencies.auth import get_current_user, verify_token
from webhookhub.db.models.user import UserModel
from webhookhub.db.session import get_db_session
from webhookhub.schemas.api_key import APIKeyCreateSchema, APIKeyResponseSchema
from webhookhub.schemas.user import UserResponseSchema
from webhookhub.services.api_key_service import create_api_key



router = APIRouter( prefix="/v1/api-keys", tags=["API Keys"],)


@router.post( "/generate", response_model=APIKeyResponseSchema, status_code=status.HTTP_201_CREATED,)
async def generate_api_key( payload: APIKeyCreateSchema,current_user: UserModel = Depends(verify_token), session: AsyncSession = Depends(get_db_session) ):

    api_key_model, api_key = await create_api_key(
        session=session,
        user_id=current_user.id,
        name=payload.name,
    )

    return {
        "id": str(api_key_model.id),
        "name": api_key_model.name,
        "key": api_key,
        "key_prefix": api_key_model.key_prefix,
        "created_at": api_key_model.created_at,
    }

@router.get("/test-api",response_model=UserResponseSchema)
def test_api(curr_user=Depends(get_current_user)):
    return curr_user