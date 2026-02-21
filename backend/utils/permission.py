from typing import Optional

from fastapi import Depends, HTTPException, status
from utils.jwt import get_current_user_id


async def login_required(user_id: Optional[int] = Depends(get_current_user_id)) -> int:
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未授权，请先登录",
        )
    return user_id
