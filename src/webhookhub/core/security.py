import hashlib
import secrets
from datetime import datetime,timedelta,timezone
import jwt
from typing import Dict
from argon2 import PasswordHasher
from webhookhub.core.config import get_settings



settings = get_settings()


API_KEY_PREFIX = "wh_live_"

password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password( password: str, password_hash: str,) -> bool:
    try:
        password_hasher.verify( password_hash, password, )

        return True

    except Exception:
        return False


def generate_api_key() -> str:
    random_part = secrets.token_urlsafe(32)

    return f"{API_KEY_PREFIX}{random_part}"

def get_key_prefix(api_key: str) -> str:
    return api_key[:16]

def hash_api_key(api_key: str) -> str:

    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()

def verify_api_key( provided_key: str, stored_hash: str,) -> bool:
    provided_hash = hash_api_key(provided_key)

    return secrets.compare_digest( provided_hash, stored_hash )

def create_access_token(payload:Dict):
    expiry_time=datetime.now(timezone.utc)+timedelta(minutes=settings.EXP_TIME)
    payload["exp"]=expiry_time
    token= jwt.encode(payload,settings.SECRET_KEY,settings.ALGORITHM)
    return token
