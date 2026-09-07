from datetime import datetime, timedelta, timezone


RETRY_DELAYS = [
    10,
    30,
    60,
    120,
]


def get_retry_delay(attempt_count: int) -> int | None:

    index = attempt_count - 1

    if index >= len(RETRY_DELAYS):
        return None

    return RETRY_DELAYS[index]


def get_next_attempt_at(attempt_count: int,) -> datetime | None:

    delay = get_retry_delay(attempt_count)

    if delay is None:
        return None

    return datetime.now(timezone.utc) + timedelta(
        seconds=delay
    )

def is_retryable_status(status_code: int) -> bool:
    return status_code == 429 or 500 <= status_code <= 599