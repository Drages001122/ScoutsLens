import hashlib
from typing import Optional

from sqlalchemy.orm import Session

from app.core.logger import logger
from app.core.security import generate_token
from app.exceptions.base import AuthenticationError, ConflictError, ValidationError
from app.models import User


class AuthService:
    """认证服务"""

    @staticmethod
    def register_user(
        db: Session, username: str, password: str, confirm_password: str
    ) -> tuple[User, str]:
        """
        用户注册

        Args:
            db: 数据库会话
            username: 用户名
            password: 密码
            confirm_password: 确认密码

        Returns:
            (用户对象, 访问令牌)

        Raises:
            ValidationError: 参数验证失败
            ConflictError: 用户名已存在
        """
        logger.info(f"注册请求: username={username}")

        if not username or not password or not confirm_password:
            raise ValidationError("用户名、密码和确认密码不能为空")

        if password != confirm_password:
            raise ValidationError("两次输入的密码不一致")

        existing_user = db.query(User).filter_by(username=username).first()
        if existing_user:
            raise ConflictError("用户名已存在")

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        new_user = User(username=username, password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        token = generate_token(new_user.id)
        logger.info(f"用户注册成功: user_id={new_user.id}")
        return new_user, token

    @staticmethod
    def login_user(db: Session, username: str, password: str) -> tuple[User, str]:
        """
        用户登录

        Args:
            db: 数据库会话
            username: 用户名
            password: 密码

        Returns:
            (用户对象, 访问令牌)

        Raises:
            ValidationError: 参数验证失败
            AuthenticationError: 认证失败
        """
        logger.info(f"登录请求: username={username}")

        if not username or not password:
            raise ValidationError("用户名和密码不能为空")

        user = db.query(User).filter_by(username=username).first()
        if not user:
            raise AuthenticationError("用户名或密码错误")

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if user.password != hashed_password:
            raise AuthenticationError("用户名或密码错误")

        token = generate_token(user.id)
        logger.info(f"用户登录成功: user_id={user.id}")
        return user, token

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        通过ID获取用户

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            用户对象，不存在返回None
        """
        return db.query(User).get(user_id)
