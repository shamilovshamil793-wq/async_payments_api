import jwt
import bcrypt
import os
from datetime import datetime, timedelta
from sanic import json
from functools import wraps

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_change_me")

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def generate_token(user_id: int, email: str, is_admin: bool = False) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "is_admin": is_admin,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return None

def protected():
    def decorator(f):
        @wraps(f)
        async def decorated(request, *args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return json({"error": "Missing or invalid token"}, status=401)
            token = auth_header.split(" ")[1]
            payload = decode_token(token)
            if not payload:
                return json({"error": "Invalid or expired token"}, status=401)
            request.ctx.user = payload
            return await f(request, *args, **kwargs)
        return decorated
    return decorator
