from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from webhookhub.db.session import get_db_session


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/db")
async def database_health_check(
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    await session.execute(text("SELECT 1"))

    return {"status": "ok"}