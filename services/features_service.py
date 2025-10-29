# api/services/features_service.py
from __future__ import annotations
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from db import db

# Aliases para el negocio de reventa de cerdos
ALIAS_ADQUISICION = {"adquisición", "adquisicion", "compra", "precio_compra"}
ALIAS_LOGISTICA   = {"logística", "logistica", "transporte", "flete", "peajes", "combustible"}
ALIAS_ALIMENTACION = {"alimentación", "alimentacion", "comida", "pienso"}

def _norm(s: Optional[str]) -> str:
    return (s or "").strip().lower()

async def _sum_por_tipocosto(id_lote: int) -> Dict[str, float]:
    costos = await db.costo.find_many(
        where={"id_lote": id_lote},
        include={"tipo_costo": True},
    )
    totales: Dict[str, float] = {}
    for c in costos:
        nombre = _norm(c.tipo_costo.nombre_tipo)
        totales[nombre] = totales.get(nombre, 0.0) + float(c.monto or 0.0)
    return totales

async def _sum_por_categoria(id_lote: int) -> Dict[str, float]:
    costos = await db.costo.find_many(
        where={"id_lote": id_lote},
        include={"tipo_costo": True},
    )
    tot = {"FIJO": 0.0, "VARIABLE": 0.0}
    for c in costos:
        cat = (c.tipo_costo.categoria or "").upper()
        if cat in tot:
            tot[cat] += float(c.monto or 0.0)
    return tot

async def build_features_para_modelo(id_lote: int) -> Dict[str, Any]:
    lote = await db.lote.find_unique(where={"id_lote": id_lote})
    if lote is None:
        raise ValueError("lote_not_found")

    # Sumas por tipo (para obtener adquisición, logística y alimentación)
    sum_by_tipo = await _sum_por_tipocosto(id_lote)

    total_adquisicion = sum(sum_by_tipo.get(n, 0.0) for n in sum_by_tipo if _norm(n) in ALIAS_ADQUISICION)
    total_logistica   = sum(sum_by_tipo.get(n, 0.0) for n in sum_by_tipo if _norm(n) in ALIAS_LOGISTICA)
    total_alimentacion = sum(sum_by_tipo.get(n, 0.0) for n in sum_by_tipo if _norm(n) in ALIAS_ALIMENTACION)

    # Sumas por categoría (para negocio)
    by_cat = await _sum_por_categoria(id_lote)
    costo_fijo_total     = float(by_cat.get("FIJO", 0.0))
    costo_variable_total = float(by_cat.get("VARIABLE", 0.0))

    # --- NUEVO: Calcular costo_alimentacion basado en estadía ---
    dias_estadia = lote.duracion_estadia_dias if lote.duracion_estadia_dias else 0
    if dias_estadia > 0:
        # Usar el costo diario validado en la entrevista (Bs 1.5/día/cerdo)
        costo_alimentacion_estadia = float(lote.cantidad_animales * dias_estadia * 1.5)
        total_alimentacion += costo_alimentacion_estadia
    # --- FIN NUEVO ---

    # Pesos y mes
    mes_adq = int(lote.fecha_adquisicion.month)
    kilos_entrada = float(lote.cantidad_animales) * float(lote.peso_promedio_entrada)

    # Si existe producción, preferimos kilos reales de salida
    produccion = await db.produccion.find_unique(where={"id_lote": id_lote})
    kilos_salida = float(produccion.peso_salida_total) if produccion else kilos_entrada

    # precio_compra_kg: usar el campo directo de la BD o calcular si no existe
    precio_compra_kg = float(lote.precio_compra_kg or 0.0)
    if precio_compra_kg == 0.0 and kilos_entrada > 0:
        precio_compra_kg = total_adquisicion / kilos_entrada

    # Calcular costo_total_lote (CTL) - feature engineering del diseño académico
    costo_total_lote = total_adquisicion + total_logistica + total_alimentacion
    
    # Features para el modelo ML (9 features - alineado con entrenamiento)
    features = {
        "cantidad_animales": float(lote.cantidad_animales),           # Nivel I
        "peso_promedio_entrada": float(lote.peso_promedio_entrada),   # Nivel I
        "precio_compra_kg": float(precio_compra_kg),                  # Nivel I
        "costo_logistica_total": float(total_logistica),              # Nivel II (renombrado para consistencia)
        "costo_alimentacion_estadia": float(total_alimentacion),       # Nivel II (renombrado para consistencia)
        "duracion_estadia_dias": float(dias_estadia),                 # Nivel II
        "mes_adquisicion": mes_adq,                                   # Nivel II
        "costo_total_lote": float(costo_total_lote),                  # Feature engineering (CTL)
        "peso_salida": float(kilos_salida),                          # Feature adicional
    }

    return {
        "lote_id": id_lote,
        "features": features,  # 9 features para el modelo ML
        "extras": {
            "costo_fijo_total": float(costo_fijo_total),
            "costo_variable_total": float(costo_variable_total),
            "kilos_entrada": float(kilos_entrada),
            "peso_salida_total": float(kilos_salida),  # Asegurar que este valor existe
            "total_adquisicion": float(total_adquisicion),
            "total_logistica": float(total_logistica),
            "total_alimentacion": float(total_alimentacion),
            "dias_estadia": dias_estadia,
        },
    }
