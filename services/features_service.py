# api/services/features_service.py
from __future__ import annotations
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
from db import db

def _parse_iso_date(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    s = s.strip().removesuffix("Z")
    # "YYYY-MM-DD" primero
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except Exception:
        pass
    # ISO completo
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

async def _lote_exists(id_lote: int) -> bool:
    return await db.lote.find_unique(where={"id_lote": id_lote}) is not None

async def _sum_costos_lote(
    id_lote: int,
    desde: Optional[str] = None,
    hasta: Optional[str] = None,
    with_detalle: bool = False,
) -> Tuple[Dict[str, float], Optional[list[dict]]]:
    """
    Suma costos por categoría FIJO / VARIABLE (según TipoCosto.categoria).
    Opcionalmente devuelve desglose por tipo.
    """
    if not await _lote_exists(id_lote):
        raise ValueError("lote_not_found")

    where = {"id_lote": id_lote}

    d = _parse_iso_date(desde)
    h = _parse_iso_date(hasta)
    if d or h:
        rango = {}
        if d:
            rango["gte"] = d
        if h:
            rango["lte"] = h
        where["fecha_gasto"] = rango

    costos = await db.costo.find_many(
        where=where,
        include={"tipo_costo": True},
        order={"fecha_gasto": "asc"},
    )

    totales = {"FIJO": 0.0, "VARIABLE": 0.0}
    by_tipo = {}  # id_tipo_costo -> dict acumulado

    for c in costos:
        monto = float(c.monto or 0.0)
        cat = (c.tipo_costo.categoria or "").upper()
        if cat in totales:
            totales[cat] += monto

        if with_detalle:
            key = c.id_tipo_costo
            if key not in by_tipo:
                by_tipo[key] = {
                    "id_tipo_costo": c.id_tipo_costo,
                    "nombre_tipo": c.tipo_costo.nombre_tipo,
                    "categoria": cat,
                    "total": 0.0,
                }
            by_tipo[key]["total"] += monto

    detalle_list = None
    if with_detalle:
        detalle_list = list(by_tipo.values())
        detalle_list.sort(key=lambda x: x["total"], reverse=True)
        for dct in detalle_list:
            dct["total"] = round(dct["total"], 4)

    # redondeo final totales
    totales = {k: round(v, 4) for k, v in totales.items()}
    return totales, detalle_list

async def build_features_para_modelo(
    id_lote: int,
    desde: Optional[str] = None,
    hasta: Optional[str] = None,
    with_detalle: bool = False,
) -> Dict[str, Any]:
    """
    Construye el paquete de features alineado al análisis:
    - Features (Nivel I–II): solo VARIABLES
    - Extras (no-modelo): FIJOS (se suman luego en backend)
    - Metadata de periodo y lote
    """
    lote = await db.lote.find_unique(where={"id_lote": id_lote})
    if lote is None:
        raise ValueError("lote_not_found")

    totales, detalle = await _sum_costos_lote(
        id_lote=id_lote,
        desde=desde,
        hasta=hasta,
        with_detalle=with_detalle,
    )

    costo_variable_total = float(totales.get("VARIABLE", 0.0))
    costo_fijo_total = float(totales.get("FIJO", 0.0))

    # Señales básicas del lote
    duracion = int(lote.duracion_ciclo_dias or 0)
    mes_adq = int(lote.fecha_adquisicion.month)

    features = {
        # Lote
        "cantidad_animales": int(lote.cantidad_animales),
        "peso_promedio_entrada": float(lote.peso_promedio_entrada),
        "duracion_ciclo_dias": duracion,
        "mes_adquisicion": mes_adq,

        # Costos de entrenamiento (Nivel I–II): agregamos VARIABLE
        "costo_variable_total": float(costo_variable_total),
    }

    bundle: Dict[str, Any] = {
        "lote_id": id_lote,
        "period": {"desde": desde, "hasta": hasta},
        "features": features,
        "extras": {
            # No entra al modelo; backend lo suma al final por kg o por política
            "costo_fijo_total": float(costo_fijo_total),
        },
        "totals": {
            "VARIABLE": round(costo_variable_total, 4),
            "FIJO": round(costo_fijo_total, 4),
            "TOTAL": round(costo_variable_total + costo_fijo_total, 4),
        },
    }

    if with_detalle and detalle is not None:
        bundle["by_tipo"] = detalle

    return bundle
