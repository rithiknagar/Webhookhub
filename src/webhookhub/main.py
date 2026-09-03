from fastapi import FastAPI

from webhookhub.api.routes.health import router as health_router
from webhookhub.core.config import get_settings


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Reliable webhook delivery platform",
)

app.include_router(health_router)