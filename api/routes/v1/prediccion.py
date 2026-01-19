from flask import Blueprint, jsonify, request
from flask_pydantic import validate
from pydantic import BaseModel, Field
from utils.auth_guard import require_jwt
from services.features_service import build_features_24_xgboost
from db import db
from config import settings
import asyncio, os, pickle
import pandas as pd

bp = Blueprint("prediccion_v1", __name__)

class PredictBody(BaseModel):
    id_lote: int = Field(gt=0)
    margen_rate: float | None = Field(default=None, ge=0.0, le=1.0, description="Margen de ganancia (0.0-1.0). Si no se especifica, usa el margen por defecto.")

def load_xgboost_model():
    """
    Carga el modelo XGBoost con 24 features.
    Retorna: (modelo, metricas_cv, metricas_full, metadata)
    """
    path = settings.MODEL_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Modelo no encontrado en: {path}")
    
    try:
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
    except Exception as e:
        raise ValueError(f"Error al cargar el modelo: {str(e)}")
    
    # El modelo XGBoost se guarda como diccionario
    if isinstance(model_data, dict):
        return (
            model_data['modelo'],
            model_data.get('metricas_cv', {}),
            model_data.get('metricas_full', {}),
            {
                'version': model_data.get('version', '1.0'),
                'fecha_entrenamiento': model_data.get('fecha_entrenamiento'),
                'n_features': model_data.get('n_features', 24)
            }
        )
    else:
        # Fallback para modelos legacy
        return model_data, {}, {}, {'version': 'legacy', 'n_features': 10}

@bp.post("/lotes/predict")
@require_jwt
@validate()
def predict_lote(body: PredictBody):
    async def _run():
        await db.connect()

        # Construir las 24 features usando el nuevo servicio
        bundle = await build_features_24_xgboost(body.id_lote, with_detalle=True)
        features_dict = bundle["features"]
        extras = bundle["extras"]
        detalle = bundle.get("detalle", {})

        # Construir vector de features en el orden correcto (24 features)
        X_dict = {
            # Grupo 1: Adquisicion
            "cantidad_animales": features_dict["cantidad_animales"],
            "peso_promedio_entrada": features_dict["peso_promedio_entrada"],
            "precio_compra_kg": features_dict["precio_compra_kg"],
            "costo_adquisicion_total": features_dict["costo_adquisicion_total"],
            
            # Grupo 2: Logistica
            "costo_combustible_viaje": features_dict["costo_combustible_viaje"],
            "costo_peajes_lavado": features_dict["costo_peajes_lavado"],
            "costo_flete_estimado": features_dict["costo_flete_estimado"],
            "mantenimiento_camion_prorrateado": features_dict["mantenimiento_camion_prorrateado"],
            
            # Grupo 3: Costos Fijos Dinamicos
            "costo_fijo_diario_lote": features_dict["costo_fijo_diario_lote"],
            "factor_ocupacion_granja": features_dict["factor_ocupacion_granja"],
            "tasa_consumo_energia_agua": features_dict["tasa_consumo_energia_agua"],
            "costo_mano_obra_asignada": features_dict["costo_mano_obra_asignada"],
            
            # Grupo 4: Estadia
            "duracion_estadia_dias": features_dict["duracion_estadia_dias"],
            "costo_alimentacion_total": features_dict["costo_alimentacion_total"],
            "costo_sanitario_total": features_dict["costo_sanitario_total"],
            "merma_peso_transporte": features_dict["merma_peso_transporte"],
            "peso_salida_esperado": features_dict["peso_salida_esperado"],
            
            # Grupo 5: Temporales
            "mes_adquisicion": features_dict["mes_adquisicion"],
            "dia_semana_llegada": features_dict["dia_semana_llegada"],
            "es_feriado_proximo": features_dict["es_feriado_proximo"],
            "dias_para_festividad": features_dict["dias_para_festividad"],
            
            # Grupo 6: Compuestas
            "costo_operativo_por_cabeza": features_dict["costo_operativo_por_cabeza"],
            "ratio_alimento_precio_compra": features_dict["ratio_alimento_precio_compra"],
            "indicador_eficiencia_estadia": features_dict["indicador_eficiencia_estadia"],
        }
        
        # Convertir a DataFrame (XGBoost espera DataFrame)
        X = pd.DataFrame([X_dict])

        # CARGAR Y USAR EL MODELO XGBOOST
        modelo, metricas_cv, metricas_full, metadata = load_xgboost_model()
        
        # Prediccion con XGBoost
        precio_ml_predicho = float(modelo.predict(X)[0])
        
        # Aplicar margen adicional si el usuario lo especifica
        margen_rate = float(body.margen_rate) if body.margen_rate is not None else float(settings.DEFAULT_MARGIN_RATE)
        precio_sugerido_kg = precio_ml_predicho * (1.0 + margen_rate)
        margen_valor_kg = precio_ml_predicho * margen_rate

        # Calculos de costos y ganancia
        kilos_salida = float(extras["peso_salida_total"])
        costo_variable_total = float(extras["costo_variable_total"])
        costo_fijo_total = float(extras["costo_fijo_total"])
        costo_total = costo_variable_total + costo_fijo_total
        
        ingreso_total = precio_sugerido_kg * kilos_salida
        ganancia_neta_estimada = ingreso_total - costo_total

        # Obtener usuario del JWT
        payload = getattr(request, "user", {})
        id_usuario = payload.get("uid")

        # Guardar prediccion en BD con MAE
        mae_modelo = metricas_cv.get('mae_mean', 0.0)
        pred = await db.prediccion.create(
            data={
                "id_lote": body.id_lote,
                "precio_sugerido_kg": precio_sugerido_kg,
                "modelo_usado": f"XGBoost v{metadata['version']}",
                "ganancia_neta_estimada": ganancia_neta_estimada,
                "id_usuario_realiza": id_usuario if id_usuario else None,
                "mae_error": mae_modelo,  # NUEVO: Guardar MAE del modelo
            }
        )

        await db.disconnect()
        
        # Preparar mensaje de estacionalidad
        mensaje_estacionalidad = None
        if features_dict["es_feriado_proximo"]:
            dias = features_dict["dias_para_festividad"]
            if dias <= 3:
                mensaje_estacionalidad = f"⚠️ Ajuste aplicado: Festividad en {dias} días (alta demanda)"
            else:
                mensaje_estacionalidad = f"📅 Festividad próxima en {dias} días"
        
        return {
            "lote_id": body.id_lote,
            
            # Precios
            "precio_compra_kg": round(features_dict["precio_compra_kg"], 2),
            "precio_ml_predicho": round(precio_ml_predicho, 2),  # Prediccion directa del modelo
            "precio_sugerido_kg": round(precio_sugerido_kg, 2),  # Con margen adicional
            "margen_rate": margen_rate,
            "margen_valor_kg": round(margen_valor_kg, 2),
            
            # Metricas del modelo (RIGOR CIENTIFICO)
            "modelo": {
                "nombre": f"XGBoost v{metadata['version']}",
                "mae": round(mae_modelo, 4),  # Error Absoluto Medio
                "r2": round(metricas_cv.get('r2_mean', 0.0), 4),  # R² del modelo
                "n_features": metadata['n_features'],
                "fecha_entrenamiento": metadata.get('fecha_entrenamiento'),
            },
            
            # Desglose de costos indirectos (TRANSPARENCIA)
            "desglose_costos_indirectos": {
                "tasa_consumo_energia_agua": round(features_dict["tasa_consumo_energia_agua"], 2),
                "costo_mano_obra_asignada": round(features_dict["costo_mano_obra_asignada"], 2),
                "costo_fijo_diario_lote": round(features_dict["costo_fijo_diario_lote"], 2),
                "factor_ocupacion_granja": round(features_dict["factor_ocupacion_granja"], 4),
            },
            
            # Estacionalidad
            "estacionalidad": {
                "mes_adquisicion": features_dict["mes_adquisicion"],
                "es_feriado_proximo": bool(features_dict["es_feriado_proximo"]),
                "dias_para_festividad": features_dict["dias_para_festividad"],
                "mensaje": mensaje_estacionalidad,
            },
            
            # Ganancia
            "ganancia_neta_estimada": round(ganancia_neta_estimada, 2),
            "costo_total": round(costo_total, 2),
            "ingreso_total": round(ingreso_total, 2),
            
            # Metadata
            "prediccion_id": pred.id_prediccion,
            "kilos_salida": round(kilos_salida, 2),
            
            # Desglose completo (opcional, para debugging)
            "detalle_grupos": detalle if detalle else None,
        }

    try:
        result = asyncio.run(_run())
        return jsonify(result), 200
    except FileNotFoundError as e:
        return jsonify(error=str(e)), 500
    except Exception as e:
        return jsonify(error=str(e)), 500
