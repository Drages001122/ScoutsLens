import hashlib

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config import get_db
from models import (
    AuthResponse,
    ErrorResponse,
    User,
    UserCreate,
    UserLogin,
    UserResponse,
)
from utils.jwt import generate_token, get_current_user_id

router = APIRouter()


@router.post(
    "/register",
    response_model=AuthResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def register(data: UserCreate, db: Session = Depends(get_db)):
    try:
        if not data.username or not data.password or not data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名、密码和确认密码不能为空",
            )
        if data.password != data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="两次输入的密码不一致",
            )
        existing_user = db.query(User).filter_by(username=data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在",
            )
        hashed_password = hashlib.sha256(data.password.encode()).hexdigest()
        new_user = User(username=data.username, password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        token = generate_token(new_user.id)
        return AuthResponse(
            message="注册成功",
            user=UserResponse(**new_user.to_dict()),
            token=token,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def login(data: UserLogin, db: Session = Depends(get_db)):
    try:
        if not data.username or not data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名和密码不能为空",
            )
        user = db.query(User).filter_by(username=data.username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
            )
        hashed_password = hashlib.sha256(data.password.encode()).hexdigest()
        if user.password != hashed_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
            )
        token = generate_token(user.id)
        return AuthResponse(
            message="登录成功",
            user=UserResponse(**user.to_dict()),
            token=token,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/me",
    response_model=UserResponse,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未提供认证令牌",
            )
        user = db.query(User).get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在",
            )
        return UserResponse(**user.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
