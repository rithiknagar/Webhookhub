import asyncio
from datetime import datetime, timezone,timedelta

from sqlalchemy import select

from webhookhub.db.session import AsyncSessionLocal
from webhookhub.db.models.delivery import DeliveryModel
from webhookhub.worker.tasks import deliver_webhook
from webhookhub.db.worker_session import WorkerSessionLocal
from webhookhub.worker.celery_app import celery_app
from webhookhub.worker.tasks import max_attempts

PROCESSING_TIMEOUT = timedelta(minutes=5)

async def process_due_deliveries():

    async with WorkerSessionLocal() as db:

        result = await db.execute(
            select(DeliveryModel)
            .where(
                DeliveryModel.status == "retry_pending",
                DeliveryModel.next_attempt_at <= datetime.now(timezone.utc),
            )
            .with_for_update(          # Make claiming atomic  
                skip_locked=True
            )
        )

        deliveries = result.scalars().all()

        delivery_ids = []

        for delivery in deliveries:

            delivery.status = "pending"
            delivery.next_attempt_at = None

            delivery_ids.append(
                str(delivery.id)
            )

        await db.commit()

    for delivery_id in delivery_ids:

        deliver_webhook.delay(
            delivery_id
        )


async def recover_stale_deliveries():

    cutoff_time = (datetime.now(timezone.utc)- PROCESSING_TIMEOUT)

    async with WorkerSessionLocal() as db:

        result = await db.execute(
            select(DeliveryModel)
            .where(
                DeliveryModel.status == "processing",
                DeliveryModel.last_attempt_at < cutoff_time,
            )
            .with_for_update(
                skip_locked=True
            )
        )

        deliveries = result.scalars().all()
        

        for delivery in deliveries:

            if delivery.attempt_count >= max_attempts:
                delivery.status = "exhausted"
                delivery.next_attempt_at = None
            else:
                delivery.status = "retry_pending"
                delivery.next_attempt_at = datetime.now(timezone.utc)

                delivery.last_error = (
                    "Delivery processing timed out"
                )

        await db.commit()


@celery_app.task
def schedule_due_deliveries():

    asyncio.run( process_due_deliveries())

@celery_app.task
def recover_stale_deliveries_task():

    asyncio.run(recover_stale_deliveries())