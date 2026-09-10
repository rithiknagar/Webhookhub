from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from webhookhub.services.health_service import check_database, check_redis
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

@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db_session)):
    database_ok = await check_database(db)
    redis_ok = await check_redis()

    if not database_ok or not redis_ok:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not_ready",
                "database": database_ok,
                "redis": redis_ok,
            })

    return {
        "status": "ready",
        "database": True,
        "redis": True,
    }