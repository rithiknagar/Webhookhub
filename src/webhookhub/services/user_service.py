from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from webhookhub.db.models.user import UserModel
from webhookhub.schemas.user import UserCreateSchema
from webhookhub.core.security import hash_password, verify_password, create_access_token
from fastapi.security import APIKeyHeader
from webhookhub.core.config import get_settings

setting=get_settings()

authorization_header = APIKeyHeader(name="Authorization", auto_error=False)

async def create_user(session : AsyncSession, body:UserCreateSchema )->UserModel:
    result= await session.execute(
        select(UserModel).where(UserModel.email==body.email)
    )
    existing_user=result.scalar_one_or_none()

    if existing_user:
        raise ValueError("User with this email already exists")

    user=UserModel(
        email=body.email,
        password_hash=hash_password(body.password)
    )

    session.add(user)

    await session.commit()
    await session.refresh(user)

    return user

async def login_user( body:UserCreateSchema,session : AsyncSession,):
   
        result= await session.execute(
            select(UserModel).where(UserModel.email==body.email)
        )
        user= result.scalar_one_or_none()

        if not user:
            raise  ValueError("Incorrect email or password")
    
        verify_pass=verify_password(body.password, user.password_hash)
    
        if not verify_pass:
            raise ValueError("Incorrect email or password")
    
        payload={
            "id":str(user.id),
            "email":user.email,
        }
        token=create_access_token(payload)
        print(token)
    
        return token

