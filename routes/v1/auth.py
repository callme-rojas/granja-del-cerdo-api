from flask import Blueprint, request, jsonify
import jwt, time
from config import settings
from services.auth_service import get_user_by_email, verify_password

bp = Blueprint("auth_v1", __name__)

# Generar token JWT
def make_token(sub: str, uid: int, role_id: int):
    now = int(time.time())
    payload = {
        "sub": sub,
        "uid": uid,
        "role": role_id,
        "iat": now,
        "exp": now + 3600,  # 1 hora
        "iss": "granja-del-cerdo-api",
        "aud": "granja-ui",
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

# Endpoint: /api/v1/login
@bp.post("/login")
def login():
    import asyncio
    
    async def _login():
        try:
            data = request.get_json() or {}
            email = (data.get("email") or "").strip().lower()
            password = data.get("password") or ""

            if not email or not password:
                return jsonify(error="email_and_password_required"), 400

            # Buscar usuario con Prisma
            user = await get_user_by_email(email)
            if not user or not verify_password(password, user.password_hash):
                return jsonify(error="invalid_credentials"), 401

            # Generar token JWT
            token = make_token(user.email, user.id_usuario, user.id_rol or 0)

            return jsonify(
                access_token=token,
                user={
                    "id": user.id_usuario,
                    "email": user.email,
                    "name": user.nombre_completo,
                    "role": user.id_rol,
                },
            )
        except Exception as e:
            print(f"Error en login: {e}")
            return jsonify(error=str(e)), 500
    
    try:
        return asyncio.run(_login())
    except Exception as e:
        print(f"Error en asyncio.run: {e}")
        return jsonify(error="internal_server_error"), 500
