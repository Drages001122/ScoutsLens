import os
from datetime import datetime, timedelta

import jwt
from flask import request

SECRET_KEY = os.environ.get("SECRET_KEY")
assert SECRET_KEY, "SECRET_KEY environment variable is not set"


def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=7),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user_id():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return None
    user_id = verify_token(token)
    return user_id
