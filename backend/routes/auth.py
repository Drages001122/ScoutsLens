import hashlib

from config import db
from flask import Blueprint, jsonify, request
from models import User
from utils.jwt import generate_token, verify_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        if not username or not password or not confirm_password:
            return jsonify({"error": "用户名、密码和确认密码不能为空"}), 400
        if password != confirm_password:
            return jsonify({"error": "两次输入的密码不一致"}), 400
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({"error": "用户名已存在"}), 400
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
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
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return jsonify({"error": "用户名和密码不能为空"}), 400
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"error": "用户名或密码错误"}), 401
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if user.password != hashed_password:
            return jsonify({"error": "用户名或密码错误"}), 401
        token = generate_token(user.id)
        return (
            jsonify({"message": "登录成功", "user": user.to_dict(), "token": token}),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "未提供认证令牌"}), 401
        user_id = verify_token(token)
        if not user_id:
            return jsonify({"error": "无效的认证令牌"}), 401
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "用户不存在"}), 404
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
