from typing import Any, Dict, List, Optional


class PaginationError(Exception):
    """分页错误基类"""
    pass


class InvalidPageError(PaginationError):
    """无效页码错误"""
    pass


class InvalidPerPageError(PaginationError):
    """无效每页数量错误"""
    pass


def paginate(
    items: List[Any],
    page: int,
    per_page: int,
    items_key: str = "items",
    max_per_page: Optional[int] = None,
) -> Dict[str, Any]:
    """
    对列表进行分页处理

    Args:
        items: 待分页的列表
        page: 当前页码（从1开始）
        per_page: 每页数量
        items_key: 返回结果中数据项的键名，默认为"items"
        max_per_page: 每页最大数量限制，None表示不限制

    Returns:
        包含分页数据和分页信息的字典

    Raises:
        InvalidPageError: 页码无效时抛出
        InvalidPerPageError: 每页数量无效时抛出

    Examples:
        >>> items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        >>> paginate(items, page=1, per_page=3)
        {
            'items': [1, 2, 3],
            'pagination': {
                'current_page': 1,
                'per_page': 3,
                'total_items': 10,
                'total_pages': 4
            }
        }
    """
    if page < 1:
        raise InvalidPageError(f"页码必须大于等于1，当前值: {page}")

    if per_page < 1:
        raise InvalidPerPageError(f"每页数量必须大于等于1，当前值: {per_page}")

    if max_per_page is not None and per_page > max_per_page:
        raise InvalidPerPageError(
            f"每页数量不能超过{max_per_page}，当前值: {per_page}"
        )

    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page if per_page > 0 else 0

    if page > total_pages and total_pages > 0:
        raise InvalidPageError(
            f"页码超出范围，最大页码为{total_pages}，当前值: {page}"
        )

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


def paginate_with_metadata(
    items: List[Any],
    page: int,
    per_page: int,
    items_key: str = "items",
    max_per_page: Optional[int] = None,
    **metadata,
) -> Dict[str, Any]:
    """
    对列表进行分页处理，并添加额外的元数据

    Args:
        items: 待分页的列表
        page: 当前页码（从1开始）
        per_page: 每页数量
        items_key: 返回结果中数据项的键名，默认为"items"
        max_per_page: 每页最大数量限制，None表示不限制
        **metadata: 额外的元数据，将直接添加到返回结果中

    Returns:
        包含分页数据、分页信息和额外元数据的字典

    Examples:
        >>> items = [1, 2, 3, 4, 5]
        >>> paginate_with_metadata(items, page=1, per_page=2, game_date="2024-01-01")
        {
            'items': [1, 2],
            'pagination': {
                'current_page': 1,
                'per_page': 2,
                'total_items': 5,
                'total_pages': 3
            },
            'game_date': '2024-01-01'
        }
    """
    result = paginate(items, page, per_page, items_key, max_per_page)
    result.update(metadata)
    return result


def get_pagination_info(
    total_items: int, page: int, per_page: int
) -> Dict[str, int]:
    """
    获取分页信息（不进行实际切片）

    Args:
        total_items: 总项目数
        page: 当前页码（从1开始）
        per_page: 每页数量

    Returns:
        包含分页信息的字典

    Examples:
        >>> get_pagination_info(100, 3, 10)
        {
            'current_page': 3,
            'per_page': 10,
            'total_items': 100,
            'total_pages': 10,
            'has_next': True,
            'has_previous': True
        }
    """
    total_pages = (total_items + per_page - 1) // per_page if per_page > 0 else 0

    return {
        "current_page": page,
        "per_page": per_page,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def calculate_offset(page: int, per_page: int) -> int:
    """
    计算数据库查询的偏移量

    Args:
        page: 当前页码（从1开始）
        per_page: 每页数量

    Returns:
        偏移量（从0开始）

    Examples:
        >>> calculate_offset(2, 10)
        10
    """
    return (page - 1) * per_page


def validate_pagination_params(
    page: int, per_page: int, max_per_page: Optional[int] = None
) -> None:
    """
    验证分页参数的有效性

    Args:
        page: 当前页码（从1开始）
        per_page: 每页数量
        max_per_page: 每页最大数量限制，None表示不限制

    Raises:
        InvalidPageError: 页码无效时抛出
        InvalidPerPageError: 每页数量无效时抛出
    """
    if page < 1:
        raise InvalidPageError(f"页码必须大于等于1，当前值: {page}")

    if per_page < 1:
        raise InvalidPerPageError(f"每页数量必须大于等于1，当前值: {per_page}")

    if max_per_page is not None and per_page > max_per_page:
        raise InvalidPerPageError(
            f"每页数量不能超过{max_per_page}，当前值: {per_page}"
        )
