import hashlib
import hmac


def generate_signature(secret: str,timestamp: str,payload: bytes,) -> str:

    message = (
        timestamp.encode("utf-8")
        + b"."
        + payload
    )
    
    signature = hmac.new(
        secret.encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()

    return f"sha256={signature}"