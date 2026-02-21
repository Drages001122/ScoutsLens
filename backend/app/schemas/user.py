from typing import Optional

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    """用户响应"""

    id: int
    username: str
    created_at: Optional[str] = None


class UserCreate(BaseModel):
    """用户创建请求"""

    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)
    confirm_password: str = Field(..., min_length=1)


class UserLogin(BaseModel):
    """用户登录请求"""

    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class AuthResponse(BaseModel):
    """认证响应"""

    message: str
    user: UserResponse
    token: str
