from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class MessageResponse(BaseModel):
    """通用消息响应"""

    message: str


class ErrorResponse(BaseModel):
    """错误响应"""

    error: str


class Pagination(BaseModel):
    """分页信息"""

    current_page: int
    per_page: int
    total_items: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    """通用分页响应"""

    items: List[T]
    pagination: Pagination


class TeamResponse(BaseModel):
    """球队信息响应"""

    team_id: int
    team_name: str
