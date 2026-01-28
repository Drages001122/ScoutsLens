import hashlib
import os
from datetime import datetime, timedelta

import jwt
from config import db
from flask import Blueprint, jsonify, request
from models import User

# 创建蓝图
auth_bp = Blueprint("auth", __name__)

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
        return jsonify({"error": "令牌已过期"}), 401
    except jwt.InvalidTokenError:
        return None


@auth_bp.route("/register", methods=["POST"])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if not username or not password or not confirm_password:
            return jsonify({"error": "用户名、密码和确认密码不能为空"}), 400

        if password != confirm_password:
            return jsonify({"error": "两次输入的密码不一致"}), 400

        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({"error": "用户名已存在"}), 400

        # 密码哈希处理
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # 创建新用户
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # 生成令牌
        token = generate_token(new_user.id)

        return (
            jsonify(
                {"message": "注册成功", "user": new_user.to_dict(), "token": token}
            ),
            201,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "用户名和密码不能为空"}), 400

        # 查找用户
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"error": "用户名或密码错误"}), 401

        # 验证密码
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if user.password != hashed_password:
            return jsonify({"error": "用户名或密码错误"}), 401

        # 生成令牌
        token = generate_token(user.id)

        return (
            jsonify({"message": "登录成功", "user": user.to_dict(), "token": token}),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    """获取当前登录用户信息"""
    try:
        # 从请求头获取令牌
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "未提供认证令牌"}), 401

        # 验证令牌
        user_id = verify_token(token)
        if not user_id:
            return jsonify({"error": "无效的认证令牌"}), 401

        # 查找用户
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "用户不存在"}), 404

        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
