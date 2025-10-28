from flask import Blueprint, jsonify, request
from flask_pydantic import validate
from pydantic import BaseModel, Field
from utils.auth_guard import require_jwt
from services.features_service import build_features_para_modelo
from db import db
from config import settings
import asyncio, os, joblib

bp = Blueprint("prediccion_v1", __name__)

class PredictBody(BaseModel):
    id_lote: int = Field(gt=0)

def load_model():
    path = settings.MODEL_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Modelo no encontrado en: {path}")
    return joblib.load(path)

@bp.post("/lotes/predict")
@require_jwt
@validate()
def predict_lote(body: PredictBody):
    async def _run():
        await db.connect()

        bundle = await build_features_para_modelo(body.id_lote)
        f = bundle["features"]
        extras = bundle["extras"]

        # Vector de entrada EXACTO (alineado a documento)
        X = [[
            f["precio_compra_kg"],
            f["costo_logistica_total"],
            f["peso_salida_total"],
            f["mes_adquisicion"],
        ]]

        model = load_model()
        precio_base_kg = float(model.predict(X)[0])

        # Negocio: sumar fijos por kg + margen
        kilos_salida = float(extras["peso_salida_total"]) if "peso_salida_total" in f else float(extras["kilos_salida"])
        costo_fijo_total = float(extras["costo_fijo_total"])
        costo_variable_total = float(extras["costo_variable_total"])

        fijo_por_kg = (costo_fijo_total / kilos_salida) if kilos_salida else 0.0
        margen_rate = float(settings.DEFAULT_MARGIN_RATE)

        subtotal = precio_base_kg + fijo_por_kg
        precio_sugerido_kg = subtotal * (1.0 + margen_rate)

        # RF-02: Ganancia neta estimada
        ingreso_total = precio_sugerido_kg * kilos_salida
        costo_total = costo_variable_total + costo_fijo_total
        ganancia_neta_estimada = ingreso_total - costo_total

        # Obtener usuario del JWT
        payload = getattr(request, "user", {})
        id_usuario = payload.get("uid")

        pred = await db.prediccion.create(
            data={
                "id_lote": body.id_lote,
                "precio_sugerido_kg": precio_sugerido_kg,
                "modelo_usado": "latest",
                "ganancia_neta_estimada": ganancia_neta_estimada,
                "id_usuario_realiza": id_usuario if id_usuario else None,
            }
        )

        await db.disconnect()
        return {
            "lote_id": body.id_lote,
            "precio_base_kg": round(precio_base_kg, 4),
            "fijo_por_kg": round(fijo_por_kg, 4),
            "margen_rate": margen_rate,
            "precio_sugerido_kg": round(precio_sugerido_kg, 4),
            "ganancia_neta_estimada": round(ganancia_neta_estimada, 2),
            "prediccion_id": pred.id_prediccion,
        }

    try:
        result = asyncio.run(_run())
        return jsonify(result), 200
    except FileNotFoundError as e:
        return jsonify(error=str(e)), 500
    except Exception as e:
        return jsonify(error=str(e)), 500
