from webhookhub.worker.celery_app import celery_app
import asyncio
import httpx
from datetime import datetime, timezone, timedelta
from webhookhub.worker.celery_app import celery_app
from webhookhub.db.session import AsyncSessionLocal
from webhookhub.db.models.delivery import DeliveryModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from webhookhub.services.retry_service import get_next_attempt_at, is_retryable_status
from webhookhub.db.worker_session import WorkerSessionLocal
import json
import time
from webhookhub.services.url_security_service import validate_webhook_url
from webhookhub.services.webhook_signing_service import generate_signature
from webhookhub.services.delivery_service import get_next_attempt_number
from webhookhub.db.models.delivery_attempt_model import DeliveryAttemptModel
import logging

logger = logging.getLogger(__name__)

max_attempts=5

  

async def process_delivery(delivery_id: str):
    async with WorkerSessionLocal() as db:
        result = await db.execute(
            select(DeliveryModel)
            .options(
                selectinload(DeliveryModel.event),
                selectinload(DeliveryModel.endpoint),
            )
            .where(
                DeliveryModel.id == delivery_id
            )
        )

        delivery = result.scalar_one_or_none()

        if delivery is None:
            print(f"Delivery {delivery_id} not found")
            return

        event = delivery.event
        endpoint = delivery.endpoint

        print("event type",event.event_type)
        logger.info(
            "delivery_started "
            "delivery_id=%s event_id=%s endpoint_id=%s "
            "attempt=%s",
            delivery.id,
            event.event_id,
            endpoint.id,
            delivery.attempt_count,
        )

        
        delivery.status = "processing"
        delivery.attempt_count += 1
        delivery.last_attempt_at = datetime.now(timezone.utc)

        await db.commit()

        attempt_number = await get_next_attempt_number(
            db=db,
            delivery_id=delivery.id,
        )

        attempt_started_at = datetime.now(timezone.utc)

        attempt = DeliveryAttemptModel(
            delivery_id=delivery.id,
            attempt_number=attempt_number,
            started_at=attempt_started_at,
        )

        db.add(attempt)

        await db.commit()
        await db.refresh(attempt)

        try:
            async with httpx.AsyncClient(
                timeout=10.0
            ) as client:
                payload_bytes = json.dumps(
                    event.payload,
                    separators=(",", ":"),
                ).encode("utf-8")

                timestamp = str(
                    int(time.time())
                )
                signature = generate_signature(
                    secret=endpoint.secret,
                    timestamp=timestamp,
                    payload=payload_bytes,
                )
                print("secret",endpoint.secret)
                print("payload",payload_bytes)
                print("timestamp",timestamp)
                print("signature",signature)

                try:
                    validate_webhook_url(endpoint.url)

                except ValueError as exc:
                    delivery.status = "failed"
                    delivery.last_error = str(exc)
                    delivery.response_status = None

                    await db.commit()

                    return

                start_time = time.perf_counter()

                response = await client.post(
                    endpoint.url,
                    content=payload_bytes,
                    headers={
                        "Content-Type": "application/json",
                        "X-Webhook-Delivery-ID": str(delivery.id),
                        "X-Webhook-Event-ID": event.event_id,
                        "X-Webhook-Event-Type": event.event_type,
                        "X-Webhook-Timestamp": timestamp,
                        "X-Webhook-Signature": signature,
                    },
                )

                duration_ms = int((time.perf_counter() - start_time) * 1000)

            delivery.response_status = response.status_code
            delivery.last_attempt_at = datetime.now(timezone.utc)

            if 200 <= response.status_code < 300:

                attempt.completed_at = datetime.now(timezone.utc)
                attempt.response_status = response.status_code
                attempt.duration_ms = duration_ms
                attempt.error = None

                delivery.status = "succeeded"
                delivery.last_error = None
                delivery.next_attempt_at = None

                logger.info(
                    "delivery_succeeded "
                    "delivery_id=%s event_id=%s "
                    "attempt=%s response_status=%s",
                    delivery.id,
                    event.event_id,
                    delivery.attempt_count,
                    response.status_code,
                )

            elif is_retryable_status(response.status_code):

                attempt.completed_at = datetime.now(timezone.utc)
                attempt.response_status = response.status_code
                attempt.duration_ms = duration_ms
                attempt.error = f"Webhook returned HTTP {response.status_code}"

                if delivery.attempt_count >= max_attempts:

                    delivery.status = "exhausted"

                else:

                    delivery.status = "retry_pending"

                    delivery.next_attempt_at = get_next_attempt_at(
                        delivery.attempt_count
                    )

                    delivery.last_error = (
                        f"Webhook returned HTTP "
                        f"{response.status_code}"
                    )

                logger.warning(
                    "delivery_retry_scheduled "
                    "delivery_id=%s event_id=%s "
                    "attempt=%s response_status=%s "
                    "next_attempt_at=%s",
                    delivery.id,
                    event.event_id,
                    delivery.attempt_count,
                    response.status_code,
                    delivery.next_attempt_at,
                )

            else:

                attempt.completed_at = datetime.now(timezone.utc)
                attempt.response_status = response.status_code
                attempt.duration_ms = duration_ms
                attempt.error = f"Webhook returned HTTP {response.status_code}"

                delivery.status = "failed"

                delivery.next_attempt_at = None

                delivery.last_error = (
                    f"Webhook returned HTTP "
                    f"{response.status_code}"
                )

                logger.error(
                    "delivery_failed "
                    "delivery_id=%s event_id=%s "
                    "attempt=%s response_status=%s",
                    delivery.id,
                    event.event_id,
                    delivery.attempt_count,
                    response.status_code,
                )

            await db.commit()

        except httpx.RequestError as exc:

            duration_ms = int((time.perf_counter() - start_time) * 1000)

            attempt.completed_at = datetime.now(timezone.utc)
            attempt.response_status = None
            attempt.duration_ms = duration_ms
            attempt.error = str(exc)

            delivery.last_attempt_at = datetime.now(timezone.utc)
            delivery.last_error = str(exc)

            if delivery.attempt_count >= max_attempts:

                delivery.status = "exhausted"

                delivery.next_attempt_at = None

            else:

                delivery.status = "retry_pending"

                delivery.next_attempt_at = get_next_attempt_at(
                    delivery.attempt_count
                )
            logger.warning(
                "delivery_request_error "
                "delivery_id=%s event_id=%s "
                "attempt=%s error=%s",
                delivery.id,
                event.event_id,
                delivery.attempt_count,
                str(exc),
            )

            await db.commit()




@celery_app.task
def deliver_webhook(delivery_id: str):
    asyncio.run(
        process_delivery(delivery_id)
    )

@celery_app.task
def test_task(message: str):
    print(f"Worker received: {message}")

    return {
        "message": message,
    }