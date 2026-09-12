from fastapi import Depends, HTTPException, status

from webhookhub.services.rate_limit_service import check_rate_limit

from webhookhub.api.dependencies.auth import get_current_user


async def event_rate_limit(current_user=Depends( get_current_user) ):

    limit: int=3
   
    key = f"rate_limit:event:{current_user.id}"

    allowed, remaining = await check_rate_limit(
        key=key,
        limit=limit,
        window_seconds=60,
    )

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={
                "Retry-After": "60",
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
            },
        )

    return current_user