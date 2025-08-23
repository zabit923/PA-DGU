import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException
from jose import jwt
from passlib.context import CryptContext
from starlette import status

from config import JWT_ALGORITHM, settings

SECRET = settings.secret.secret_key


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_passwd_hash(password: str) -> str:
    password_hash = bcrypt_context.hash(password)
    return password_hash


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt_context.verify(password, password_hash)


def create_access_token(
    username: str, user_id: int, expires_delta: timedelta = None, refresh: bool = False
):
    payload = {
        "username": username,
        "user_id": user_id,
        "refresh": refresh,
        "exp": datetime.utcnow() + expires_delta,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    token_data = jwt.decode(token=token, key=SECRET, algorithms=[JWT_ALGORITHM])
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired."
        )
    return token_data


def generate_token(payload: dict) -> str:
    return jwt.encode(
        payload,
        key=settings.secret.secret_key,
        algorithm=JWT_ALGORITHM,
    )


def is_expired(expires_at: int) -> bool:
    current_timestamp = int(datetime.now(timezone.utc).timestamp())
    return current_timestamp > expires_at


def verify_token(token: str) -> dict:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing.",
        )
    return decode_token(token)


def validate_token_payload(
    payload: dict, expected_type: Optional[str] = None
) -> dict:
    if expected_type:
        token_type = payload.get("type")
        if token_type != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token type {token_type} does not match expected type {expected_type}",
            )
    expires_at = payload.get("expires_at")
    if is_expired(expires_at):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token has expired",
        )
    return payload


def generate_password_reset_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "type": "password_reset",
        "expires_at": (
            int(datetime.now(timezone.utc).timestamp())
            + 60 * 60
        ),
    }
    return generate_token(payload)


def validate_password_reset_token(payload: dict) -> int:
    validate_token_payload(payload, "password_reset")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"user_id {payload.get('sub')} does not match password reset token",
        )
    return user_id
