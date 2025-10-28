# api/services/features_service.py
from __future__ import annotations
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from db import db

# Ajusta estos alias según tus nombres reales en TipoCosto.nombre_tipo
ALIAS_ADQUISICION = {"adquisición", "adquisicion", "compra"}
ALIAS_LOGISTICA   = {"logística", "logistica", "transporte", "flete", "peajes", "combustible"}

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

    # Sumas por tipo (para obtener adquisición y logística)
    sum_by_tipo = await _sum_por_tipocosto(id_lote)

    total_adquisicion = sum(sum_by_tipo.get(n, 0.0) for n in sum_by_tipo if _norm(n) in ALIAS_ADQUISICION)
    total_logistica   = sum(sum_by_tipo.get(n, 0.0) for n in sum_by_tipo if _norm(n) in ALIAS_LOGISTICA)

    # Sumas por categoría (para negocio)
    by_cat = await _sum_por_categoria(id_lote)
    costo_fijo_total     = float(by_cat.get("FIJO", 0.0))
    costo_variable_total = float(by_cat.get("VARIABLE", 0.0))

    # Pesos y mes
    mes_adq = int(lote.fecha_adquisicion.month)
    kilos_entrada = float(lote.cantidad_animales) * float(lote.peso_promedio_entrada)

    # Si existe producción, preferimos kilos reales de salida
    produccion = await db.produccion.find_unique(where={"id_lote": id_lote})
    kilos_salida = float(produccion.kilos_vendidos) if produccion else kilos_entrada

    # precio_compra_kg = total de compra / kilos de entrada
    precio_compra_kg = (total_adquisicion / kilos_entrada) if kilos_entrada > 0 else 0.0

    features = {
        "precio_compra_kg": float(precio_compra_kg),
        "costo_logistica_total": float(total_logistica),
        "peso_salida_total": float(kilos_salida),
        "mes_adquisicion": mes_adq,
    }

    return {
        "lote_id": id_lote,
        "features": features,  # SOLO lo que ve el modelo
        "extras": {
            "costo_fijo_total": float(costo_fijo_total),
            "costo_variable_total": float(costo_variable_total),
            "kilos_entrada": float(kilos_entrada),
            "kilos_salida": float(kilos_salida),
            "total_adquisicion": float(total_adquisicion),
            "total_logistica": float(total_logistica),
        },
    }
