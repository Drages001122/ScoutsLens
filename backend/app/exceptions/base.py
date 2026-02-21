from typing import Optional


class ScoutsLensException(Exception):
    """基础异常类"""

    status_code: int = 500
    detail: str = "Internal server error"

    def __init__(self, detail: Optional[str] = None):
        if detail:
            self.detail = detail
        super().__init__(self.detail)


class ResourceNotFound(ScoutsLensException):
    """资源未找到异常"""

    status_code = 404
    detail = "Resource not found"


class AuthenticationError(ScoutsLensException):
    """认证失败异常"""

    status_code = 401
    detail = "Authentication failed"


class ValidationError(ScoutsLensException):
    """验证错误异常"""

    status_code = 400
    detail = "Validation error"


class ConflictError(ScoutsLensException):
    """冲突异常（资源已存在等）"""

    status_code = 409
    detail = "Conflict"
