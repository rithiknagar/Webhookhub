import redis.asyncio as redis
from webhookhub.core.config import get_settings

# redis_client = redis.from_url(
#     "redis://127.0.0.1:6379/2",
#     decode_responses=True,
# )

settings = get_settings()

redis_client = redis.from_url(
    f"{settings.redis_url}/2",
    decode_responses=True,
)




RATE_LIMIT_SCRIPT = """
local current = redis.call("INCR", KEYS[1])

if current == 1 then
    redis.call("EXPIRE", KEYS[1], ARGV[1])
end

return current
"""


async def check_rate_limit(
    key: str,
    limit: int,
    window_seconds: int,
) -> tuple[bool, int]:

    current_count = await redis_client.eval(
        RATE_LIMIT_SCRIPT,
        1,
        key,
        window_seconds,
    )

    remaining = max(
        limit - current_count,
        0,
    )

    return current_count <= limit, remaining