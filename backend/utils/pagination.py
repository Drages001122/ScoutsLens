from typing import Generic, List, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    pagination: dict


def get_pagination_params(
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(10, ge=1, le=100, description="每页数量"),
) -> dict:
    return {"page": page, "per_page": per_page}


def paginate(items: list, page: int, per_page: int, items_key: str = "items") -> dict:
    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page if per_page > 0 else 0
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_items = items[start_idx:end_idx]

    return {
        items_key: paginated_items,
        "pagination": {
            "current_page": page,
            "per_page": per_page,
            "total_items": total_items,
            "total_pages": total_pages,
        },
    }
