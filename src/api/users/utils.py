import logging
import uuid
from datetime import datetime, timedelta

from itsdangerous import URLSafeTimedSerializer
from jose import JWTError, jwt
from passlib.context import CryptContext

from config import settings

SECRET = settings.secret.secret_key
ALGORITHM = "HS256"


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
serializer = URLSafeTimedSerializer(secret_key=SECRET, salt="email-configuration")


def generate_passwd_hash(password: str) -> str:
    password_hash = bcrypt_context.hash(password)
    return password_hash


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt_context.verify(password, password_hash)


def create_access_token(
    username: str, user_id: int, expires_delta: timedelta = None, refresh: bool = False
):
    payload = {}
    payload["username"] = username
    payload["user_id"] = user_id
    payload["refresh"] = refresh
    payload["exp"] = datetime.utcnow() + expires_delta
    payload["jti"] = str(uuid.uuid4())
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(token=token, key=SECRET, algorithms=[ALGORITHM])
        return token_data
    except JWTError:
        logging.exception(JWTError)


def create_url_safe_token(data: dict):
    token = serializer.dumps(data)
    return token


def decode_url_safe_token(token: str):
    try:
        token_data = serializer.loads(token)
        return token_data
    except Exception as e:
        logging.error(str(e))
