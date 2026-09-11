from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from webhookhub.core.security import hash_api_key
from webhookhub.db.models.api_key import APIKeyModel
from webhookhub.db.models.user import UserModel
from webhookhub.db.session import get_db_session
from datetime import datetime, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from webhookhub.core.config import get_settings
from webhookhub.db.session import get_db_session

setting=get_settings()

bearer_scheme = HTTPBearer()


async def get_current_user( credentials: HTTPAuthorizationCredentials = Depends( bearer_scheme ),
                           session: AsyncSession = Depends(get_db_session),) -> UserModel:

    api_key = credentials.credentials

    key_hash = hash_api_key(api_key)

    result = await session.execute(
        select(APIKeyModel)
        .where(APIKeyModel.key_hash == key_hash)
    )

    api_key_model = result.scalar_one_or_none()

    if api_key_model is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    if api_key_model.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has been revoked",
        )

    if api_key_model.expires_at is not None:
       

        if api_key_model.expires_at <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key has expired",
            )

    user = await session.get(
        UserModel,
        api_key_model.user_id,
    )

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
        )

    api_key_model.last_used_at = datetime.now(timezone.utc)

    await session.commit()

    return user


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends( bearer_scheme ), session: AsyncSession = Depends(get_db_session)):

    try:    
        token=credentials.credentials
        if not token:
            raise HTTPException(status_code=401,detail="You are Unauthorized")
        
        token=token.split(" ")[-1]

        is_verified=jwt.decode(token,setting.secret_key,setting.algorithm)

        user_id = is_verified.get("id")

        if not user_id:
            raise HTTPException(status_code=401,detail="You are Unauthorized")

        result = await session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )

        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=401,detail="You are Unauthorized")

        return user

    except InvalidTokenError:
        raise HTTPException(status_code=401,detail="You are Unauthorized" )