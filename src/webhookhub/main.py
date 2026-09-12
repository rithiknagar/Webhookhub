from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from webhookhub.api.routes.health import router as health_router
from webhookhub.api.routes.user import router as users_router
from webhookhub.api.routes.api_keys import router as api_keys_router
from webhookhub.api.routes.webhook_endpoints import router as webhook_endpoints_router
from webhookhub.api.routes.events import router as events_router
from webhookhub.api.routes.delivery import router as delivery_router
from webhookhub.core.config import get_settings
from webhookhub.core.logging import configure_logging
from webhookhub.middleware.request_id import RequestIDMiddleware


settings = get_settings()

configure_logging()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Reliable webhook delivery platform",
)

cors_origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestIDMiddleware)

app.include_router(webhook_endpoints_router)
app.include_router(health_router)
app.include_router(users_router)
app.include_router(api_keys_router)
app.include_router(events_router)
app.include_router(delivery_router)