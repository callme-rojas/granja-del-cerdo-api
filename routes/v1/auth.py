from flask import Blueprint, request, jsonify
import jwt, time
from config import settings

bp = Blueprint("auth_v1", __name__)

def make_token(email: str):
    now = int(time.time())
    payload = {
        "sub": email,
        "iat": now,
        "exp": now + 3600,
        "iss": "granja-del-cerdo-api",
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return token

@bp.post("/login")
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    # 👇 TODO: conectar con DB (por ahora demo)
    if email and password:
        return jsonify(access_token=make_token(email))
    return jsonify(error="invalid_credentials"), 401
