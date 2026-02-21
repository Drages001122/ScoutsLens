from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from app.core.config import settings


def generate_token(user_id: int) -> str:
    """
    生成JWT访问令牌

    Args:
        user_id: 用户ID

    Returns:
        JWT令牌字符串
    """
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=settings.access_token_expire_days),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def verify_token(token: str) -> Optional[int]:
    """
    验证JWT令牌并返回用户ID

    Args:
        token: JWT令牌字符串

    Returns:
        用户ID，如果验证失败返回None
    """
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload.get("user_id")
    except JWTError:
        return None
