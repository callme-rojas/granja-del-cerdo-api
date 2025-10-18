from flask import Blueprint, jsonify, request
from flask_pydantic import validate
from schemas.predict_schema import PredictRequest
import jwt
from functools import wraps
from config import settings

bp = Blueprint("predict_v1", __name__)

def require_jwt(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify(error="missing_token"), 401
        token = auth.split(" ", 1)[1]
        try:
            jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        except Exception as e:
            return jsonify(error="invalid_token", detail=str(e)), 401
        return f(*args, **kwargs)
    return wrapper

@bp.post("/predict")
@require_jwt
@validate()
def predict(body: PredictRequest):
    precio = 24.10  # Dummy
    ganancia = (precio - body.precio_compra_kg) * body.peso_salida_total - body.costo_logistica_total
    return jsonify(precio_sugerido_kg=precio, ganancia_neta_estim=round(ganancia, 2))
