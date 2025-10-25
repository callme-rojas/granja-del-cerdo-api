from flask import Blueprint, jsonify, request
from flask_pydantic import validate
from pydantic import BaseModel, Field
from utils.auth_guard import require_jwt
from services.features_service import build_features_para_modelo
from db import db
from config import settings
import asyncio
import joblib
import os

bp = Blueprint("prediccion_v1", __name__)

# ---------------------------------------------
# 📦 MODELO Pydantic
# ---------------------------------------------
class PredictBody(BaseModel):
    id_lote: int = Field(gt=0, description="ID del lote a predecir")

# ---------------------------------------------
# ⚙️ Helper: cargar modelo
# ---------------------------------------------
def load_model():
    """Carga el modelo de ML desde el archivo especificado en config."""
    path = settings.MODEL_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Modelo no encontrado en: {path}")
    return joblib.load(path)

# ---------------------------------------------
# 🔹 POST /api/v1/lotes/predict
# ---------------------------------------------
@bp.post("/lotes/predict")
@require_jwt
@validate()
def predict_lote(body: PredictBody):
    """
    Realiza una predicción de precio para un lote.
    
    Body:
    - id_lote: ID del lote a predecir
    
    La predicción usa:
    - Features del lote (cantidad, peso, duración, costos variables)
    - Costos fijos del lote
    - Producción del lote (kilos vendidos)
    - Margen por defecto configurado
    
    Retorna:
    - precio_sugerido_kg: Precio final sugerido por kilo
    - Desglose del cálculo
    - ID de predicción guardada
    """
    async def _run():
        await db.connect()

        # 1️⃣ Verificar que el lote existe
        lote = await db.lote.find_unique(where={"id_lote": body.id_lote})
        if not lote:
            await db.disconnect()
            return None, ("lote_not_found", 404)

        # 2️⃣ Construir vector de features
        try:
            bundle = await build_features_para_modelo(body.id_lote)
        except ValueError as e:
            if str(e) == "lote_not_found":
                await db.disconnect()
                return None, ("lote_not_found", 404)
            await db.disconnect()
            return None, (str(e), 400)
        
        features = bundle["features"]
        extras = bundle["extras"]

        # 3️⃣ Preparar input X para el modelo
        X = [[
            features["cantidad_animales"],
            features["peso_promedio_entrada"],
            features["duracion_ciclo_dias"],
            features["costo_variable_total"],
            features["mes_adquisicion"],
        ]]

        # 4️⃣ Cargar y usar modelo entrenado
        try:
            model = load_model()
            precio_base_kg = float(model.predict(X)[0])
        except FileNotFoundError as e:
            await db.disconnect()
            return None, (str(e), 500)
        except Exception as e:
            await db.disconnect()
            return None, (f"Error al usar el modelo: {str(e)}", 500)

        # 5️⃣ Obtener costos fijos y producción
        costo_fijo_total = float(extras.get("costo_fijo_total", 0.0))
        produccion = await db.produccion.find_unique(where={"id_lote": body.id_lote})

        fijo_por_kg = 0.0
        kilos_vendidos = None
        if produccion and produccion.peso_salida_total:
            kilos_vendidos = float(produccion.peso_salida_total)
            if kilos_vendidos > 0:
                fijo_por_kg = costo_fijo_total / kilos_vendidos

        # 6️⃣ Calcular precio final con margen
        margen_rate = float(settings.DEFAULT_MARGIN_RATE)
        subtotal = precio_base_kg + fijo_por_kg
        precio_final_kg = subtotal * (1 + margen_rate)

        # 7️⃣ Guardar predicción en BD
        payload = getattr(request, "user", {})
        id_usuario = payload.get("uid")
        
        pred = await db.prediccion.create(
            data={
                "id_lote": body.id_lote,
                "precio_sugerido_kg": precio_final_kg,
                "modelo_usado": "latest",
                "id_usuario_realiza": id_usuario if id_usuario else None,
            }
        )

        await db.disconnect()

        # 8️⃣ Retornar resultado
        return {
            "lote_id": body.id_lote,
            "precio_base_kg": round(precio_base_kg, 4),
            "fijo_por_kg": round(fijo_por_kg, 4),
            "margen_rate": margen_rate,
            "precio_sugerido_kg": round(precio_final_kg, 4),
            "prediccion_id": pred.id_prediccion,
        }, None

    result, err = asyncio.run(_run())
    if err:
        msg, code = err
        if msg == "lote_not_found":
            return jsonify(error="Lote no encontrado"), code
        return jsonify(error=msg), code
    
    return jsonify(result), 200
