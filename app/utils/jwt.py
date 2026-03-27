import jwt
from datetime import datetime, timedelta, timezone
from typing import Any

from app.config import settings

JWT_SECRET = getattr(settings, "JWT_SECRET", "change-me")
JWT_ALGORITHM = getattr(settings, "JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = getattr(settings, "JWT_EXPIRE_MINUTES", 60)

def create_access_token(data: dict[str, Any], expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
