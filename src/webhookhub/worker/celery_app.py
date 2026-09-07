from celery import Celery
from celery.schedules import schedule       # celery Beat


celery_app = Celery(
    "webhookhub",
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/1",
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "schedule-due-deliveries": {
        "task": "webhookhub.worker.scheduler.schedule_due_deliveries",
        "schedule": 5.0,
    },
    "recover_stale_deliveries_task": {
        "task": "webhookhub.worker.scheduler.recover_stale_deliveries_task",
        "schedule": 30.0,
    },
}

celery_app.conf.imports = (
    "webhookhub.worker.tasks",
    "webhookhub.worker.scheduler"
)