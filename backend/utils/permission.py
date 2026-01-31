from functools import wraps

from flask import jsonify
from utils.jwt import get_current_user_id


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "未授权，请先登录"}), 401
        return f(*args, **kwargs)

    return decorated_function
