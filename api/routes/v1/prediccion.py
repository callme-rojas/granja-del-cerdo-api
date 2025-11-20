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

        # Vector de entrada con 10 features (incluyendo costos fijos)
        # IMPORTANTE: El modelo debe recibir costos fijos para predecir el precio correctamente
        kilos_salida = float(extras.get("peso_salida_total", 0.0))
        costo_fijo_total = float(extras.get("costo_fijo_total", 0.0))
        costo_fijo_por_kg = (costo_fijo_total / kilos_salida) if kilos_salida > 0 else 0.0
        
        X = [[
            f["cantidad_animales"],           # Nivel I
            f["peso_promedio_entrada"],       # Nivel I
            f["precio_compra_kg"],            # Nivel I
            f["costo_logistica_total"],       # Nivel II - Costo Variable
            f["costo_alimentacion_estadia"],  # Nivel II - Costo Variable
            f["duracion_estadia_dias"],       # Nivel II
            f["mes_adquisicion"],             # Nivel II
            f["costo_total_lote"],            # Feature engineering (CTL) - Costos Variables
            f["peso_salida"],                 # Feature adicional
            costo_fijo_por_kg,                # Nivel III - Costos Fijos (NUEVO)
        ]]

        # Cálculo de costos para información adicional
        costo_variable_total = float(extras.get("costo_variable_total", 0.0))  # Incluye compra + costos variables BD
        total_adquisicion = float(extras.get("total_adquisicion", 0.0))  # Solo compra de animales
        costo_variable_solo_bd = costo_variable_total - total_adquisicion  # Solo costos variables de BD (sin compra)
        precio_compra_kg = float(f["precio_compra_kg"])
        
        # Calcular costos por kg para información/desglose
        # IMPORTANTE: variable_por_kg debe ser solo los costos variables de BD (sin compra)
        # porque el precio de compra se muestra por separado
        variable_por_kg = (costo_variable_solo_bd / kilos_salida) if kilos_salida > 0 else 0.0
        
        # CARGAR Y USAR EL MODELO ML
        # El modelo predice directamente el precio_venta_final_kg considerando:
        # - Costos variables (logística, alimentación, compra)
        # - Costos fijos (por kg)
        # - Estacionalidad, cantidad, peso, etc.
        model, scaler = load_model()
        if scaler is not None:
            X_scaled = scaler.transform(X)
        else:
            X_scaled = X
        
        # PREDICCIÓN DIRECTA SIN MARGEN ADICIONAL: El modelo ML predice el precio base por kg
        precio_ml_base = float(model.predict(X_scaled)[0])
        
        margen_rate = float(body.margen_rate) if body.margen_rate is not None else float(settings.DEFAULT_MARGIN_RATE)
        
        # Aplicar margen seleccionado por el usuario al precio base
        precio_sugerido_kg = precio_ml_base * (1.0 + margen_rate)
        margen_valor_kg = precio_ml_base * margen_rate
        
        # Para desglose y transparencia
        precio_base_estimado = precio_ml_base

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
            "precio_compra_kg": round(precio_compra_kg, 4),  # Precio de compra original
            "precio_ml_base": round(precio_ml_base, 4),  # Precio base predicho por el modelo (sin margen extra)
            "precio_sugerido_kg": round(precio_sugerido_kg, 4),  # Precio final con el margen seleccionado
            "precio_base_estimado": round(precio_base_estimado, 4),  # Base para desglose (sin margen)
            "variable_por_kg": round(variable_por_kg, 4),  # Costos variables por kg (para info)
            "fijo_por_kg": round(costo_fijo_por_kg, 4),  # Costos fijos por kg (para info)
            "margen_rate": margen_rate,  # Margen usado en estimación
            "margen_valor_kg": round(margen_valor_kg, 4),
            "ganancia_neta_estimada": round(ganancia_neta_estimada, 2),
            "prediccion_id": pred.id_prediccion,
            # Información adicional para defensa académica
            "costo_variable_total": round(costo_variable_total, 2),
            "costo_fijo_total": round(costo_fijo_total, 2),
            "explicacion": "El modelo ML predice directamente el precio_venta_final_kg considerando costos variables y fijos como features. El precio sugerido es la predicción directa del modelo."
        }

    try:
        result = asyncio.run(_run())
        return jsonify(result), 200
    except FileNotFoundError as e:
        return jsonify(error=str(e)), 500
    except Exception as e:
        return jsonify(error=str(e)), 500
