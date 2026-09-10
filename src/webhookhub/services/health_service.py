from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from webhookhub.services.rate_limit_service import redis_client


async def check_database(db: AsyncSession) -> bool:
    try:
        await db.execute(
            text("SELECT 1")
        )

        return True

    except Exception:
        await db.rollback()
        return False

async def check_redis() -> bool:
    try:
        await redis_client.ping()

        return True

    except Exception:
        return False