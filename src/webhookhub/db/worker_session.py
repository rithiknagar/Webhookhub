from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from webhookhub.core.config import get_settings


settings = get_settings()

worker_engine = create_async_engine(
    settings.database_url,
    poolclass=NullPool,
)

WorkerSessionLocal = async_sessionmaker(
    bind=worker_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)