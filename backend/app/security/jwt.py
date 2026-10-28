from datetime import datetime
from datetime import timedelta

from jose import jwt

from app.core.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM
)


def create_access_token(
    data: dict,
    expires_minutes: int = 60
):

    payload = data.copy()

    payload["exp"] = (
        datetime.utcnow()
        + timedelta(minutes=expires_minutes)
    )

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )