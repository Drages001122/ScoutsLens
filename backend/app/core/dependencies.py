from typing import Dict, Generator, Optional

from app.core.security import verify_token
from app.db.session import SessionLocal
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

security = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话依赖

    Yields:
        SQLAlchemy数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[int]:
    """
    获取当前用户ID（可选）

    Args:
        credentials: HTTP认证凭证

    Returns:
        用户ID，如果未认证返回None
    """
    if not credentials:
        return None
    token = credentials.credentials
    user_id = verify_token(token)
    return user_id


async def login_required(
    user_id: Optional[int] = Depends(get_current_user_id),
) -> int:
    """
    登录要求依赖

    Args:
        user_id: 当前用户ID

    Raises:
        HTTPException: 401未授权

    Returns:
        用户ID
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未授权，请先登录",
        )
    return user_id


def get_pagination_params(
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(10, ge=1, description="每页数量"),
) -> Dict:
    """
    获取分页参数

    Args:
        page: 页码
        per_page: 每页数量

    Returns:
        包含分页参数的字典
    """
    return {"page": page, "per_page": per_page}
