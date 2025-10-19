from flask import Blueprint, jsonify
from flask_pydantic import validate
from pydantic import BaseModel, Field
from utils.auth_guard import require_jwt

bp = Blueprint("predict_v1", __name__)

class PredictRequest(BaseModel):
    id_lote: int
    precio_compra_kg: float = Field(gt=0)
    costo_logistica_total: float = Field(ge=0)
    peso_salida_total: float = Field(gt=0)

@bp.post("/predict")
@require_jwt
@validate()
def predict(body: PredictRequest):
    precio = 24.10
    ganancia = (precio - body.precio_compra_kg) * body.peso_salida_total - body.costo_logistica_total

    return jsonify(
        precio_sugerido_kg=precio,
        ganancia_neta_estim=round(ganancia, 2)
    )
