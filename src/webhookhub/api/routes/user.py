from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from webhookhub.db.session import get_db_session
from webhookhub.schemas.user import UserCreateSchema, UserResponseSchema

from webhookhub.services.user_service import create_user, login_user


router = APIRouter( prefix="/v1/users", tags=["Users"],)


@router.post( "/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED,)
async def register_user( payload: UserCreateSchema, session: AsyncSession = Depends(get_db_session),):
    try:
        user = await create_user( session=session, body=payload )

    except ValueError as exc:
        raise HTTPException( status_code=status.HTTP_409_CONFLICT, detail=str(exc), )

    return user

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(data:UserCreateSchema, session: AsyncSession = Depends(get_db_session)):
    try:
         token = await login_user( data, session )
    
    except ValueError as exc:
            raise HTTPException( status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc), )
    
    return token