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
    margen_rate: float | None = Field(default=None, ge=0.0, le=1.0, description="Margen de ganancia (0.0-1.0). Si no se especifica, usa el margen por defecto.")

def load_model():
    path = settings.MODEL_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Modelo no encontrado en: {path}")
    
    try:
        # Intentar cargar con modo binario explícito
        with open(path, 'rb') as f:
            model_data = joblib.load(f)
    except Exception as e:
        # Si falla, intentar sin contexto manager
        try:
            model_data = joblib.load(path)
        except Exception as e2:
            raise ValueError(f"Error al cargar el modelo: {str(e2)}. El archivo puede estar corrupto o incompatible con esta versión de joblib.")
    
    # El modelo guardado es un diccionario con múltiples componentes
    if isinstance(model_data, dict):
        return model_data['model'], model_data.get('scaler')
    else:
        # Fallback para modelos simples
        return model_data, None

@bp.post("/lotes/predict")
@require_jwt
@validate()
def predict_lote(body: PredictBody):
    async def _run():
        await db.connect()

        bundle = await build_features_para_modelo(body.id_lote)
        f = bundle["features"]
        extras = bundle["extras"]

        # Vector de entrada con 9 features (alineado con entrenamiento)
        X = [[
            f["cantidad_animales"],           # Nivel I
            f["peso_promedio_entrada"],       # Nivel I
            f["precio_compra_kg"],            # Nivel I
            f["costo_logistica_total"],       # Nivel II
            f["costo_alimentacion_estadia"],  # Nivel II
            f["duracion_estadia_dias"],       # Nivel II
            f["mes_adquisicion"],             # Nivel II
            f["costo_total_lote"],            # Feature engineering (CTL)
            f["peso_salida"],                 # Feature adicional
        ]]

        model, scaler = load_model()
        
        # Aplicar scaler si está disponible
        if scaler is not None:
            X_scaled = scaler.transform(X)
        else:
            X_scaled = X
            
        precio_base_kg = float(model.predict(X_scaled)[0])

        # Negocio: sumar fijos por kg + margen
        kilos_salida = float(extras.get("peso_salida_total", 0.0))  # Obtener desde extras
        costo_fijo_total = float(extras.get("costo_fijo_total", 0.0))
        costo_variable_total = float(extras.get("costo_variable_total", 0.0))

        fijo_por_kg = (costo_fijo_total / kilos_salida) if kilos_salida else 0.0
        
        # Usar margen dinámico si se proporciona, sino usar el por defecto
        margen_rate = float(body.margen_rate) if body.margen_rate is not None else float(settings.DEFAULT_MARGIN_RATE)

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
