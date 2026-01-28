import os
from datetime import datetime, timedelta

import jwt
from flask import request

# 生成JWT令牌的密钥
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key")


def generate_token(user_id):
    """生成JWT令牌"""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=7),  # 令牌有效期7天
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token):
    """验证JWT令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user_id():
    """获取当前登录用户ID"""
    # 从请求头获取令牌
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return None

    # 验证令牌
    user_id = verify_token(token)
    return user_id
