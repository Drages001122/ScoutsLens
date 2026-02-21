import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

security = HTTPBearer()

SECRET_KEY = os.environ.get("SECRET_KEY")
assert SECRET_KEY, "SECRET_KEY environment variable is not set"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


def generate_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("user_id")
    except JWTError:
        return None


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Optional[int]:
    token = credentials.credentials
    user_id = verify_token(token)
    return user_id
