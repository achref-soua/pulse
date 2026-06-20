from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _create_token(subject: str, expires_delta: timedelta, extra: dict[str, Any] | None = None) -> str:
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + expires_delta,
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: str, role: str, email: str = "", full_name: str = "") -> str:
    return _create_token(
        subject=user_id,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        extra={"role": role, "type": "access", "email": email, "full_name": full_name},
    )


def create_refresh_token(user_id: str) -> str:
    return _create_token(
        subject=user_id,
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
        extra={"type": "refresh"},
    )


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}") from e
