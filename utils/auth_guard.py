# api/utils/auth_guard.py
import jwt
from functools import wraps
from flask import request, jsonify
from config import settings

def require_jwt(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify(error="missing_token"), 401

        token = auth_header.split(" ", 1)[1]
        try:
            # 🔹 VALIDACIÓN JWT
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=["HS256"],
                issuer="granja-del-cerdo-api",
                audience="granja-ui",  # <--- debe coincidir con auth.py
            )
            request.user = payload  # opcional: guarda el usuario decodificado
        except jwt.ExpiredSignatureError:
            return jsonify(error="invalid_token", detail="Token expired"), 401
        except jwt.InvalidAudienceError:
            # si querés evitar este error temporalmente, podés usar verify_aud=False
            return jsonify(error="invalid_token", detail="Invalid audience"), 401
        except Exception as e:
            return jsonify(error="invalid_token", detail=str(e)), 401

        return f(*args, **kwargs)
    return wrapper
