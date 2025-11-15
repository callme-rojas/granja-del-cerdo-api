from flask import Blueprint, jsonify, request
from utils.auth_guard import require_jwt
from db import db
import asyncio
from datetime import datetime
import logging

bp = Blueprint("analytics_v1", __name__)
logger = logging.getLogger("analytics_v1")

# -----------------------------
# GET /dashboard/overview
# -----------------------------
@bp.get("/dashboard/overview")
@require_jwt
def dashboard_overview():
    """
    Devuelve la información consolidada del dashboard en una sola llamada.
    Incluye todos los lotes del usuario y la lista completa de costos
    (con sus tipos) asociados a esos lotes.
    """

    async def _run():
        await db.connect()
        try:
            lotes = await db.lote.find_many(
                order={"fecha_adquisicion": "desc"}
            )

            lote_ids = [lote.id_lote for lote in lotes]

            costos = []
            if lote_ids:
                costos = await db.costo.find_many(
                    where={"id_lote": {"in": lote_ids}},
                    include={"tipo_costo": True},
                    order={"fecha_gasto": "desc"}
                )

            payload = {
                "lotes": [lote.dict() for lote in lotes],
                "costos": [costo.dict() for costo in costos],
            }
            return payload, None
        finally:
            await db.disconnect()

    try:
        data, error = asyncio.run(_run())
    except Exception as exc:
        logger.exception("Error construyendo overview del dashboard: %s", exc)
        return jsonify(error="dashboard_overview_error"), 500

    if error:
        message, status = error
        return jsonify(error=message), status or 400

    return jsonify(data), 200

# -----------------------------
# Helpers
# -----------------------------
def _parse_iso_date(s: str | None) -> datetime | None:
    if not s:
        return None
    s = s.strip().removesuffix("Z")
    # Acepta "YYYY-MM-DD" o "YYYY-MM-DDTHH:MM:SS"
    for fmt in ("%Y-%m-%d",):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

async def _lote_exists(id_lote: int) -> bool:
    return await db.lote.find_unique(where={"id_lote": id_lote}) is not None


# -----------------------------
# GET /lotes/<id>/costos/aggregates
# -----------------------------
@bp.get("/lotes/<int:id_lote>/costos/aggregates")
@require_jwt
def costos_aggregates(id_lote: int):
    """
    Obtiene agregados de costos por categoría (FIJO/VARIABLE) para un lote.
    
    Query params:
    - desde: fecha inicial (opcional)
    - hasta: fecha final (opcional)
    - detalle: si incluir desglose por tipo de costo (true/false)
    """
    desde_str = request.args.get("desde")
    hasta_str = request.args.get("hasta")
    detalle_str = (request.args.get("detalle") or "").lower()

    desde = _parse_iso_date(desde_str)
    hasta = _parse_iso_date(hasta_str)
    with_detalle = detalle_str in ("1", "true", "yes", "y")

    async def _run():
        await db.connect()

        # Validar existencia de lote
        if not await _lote_exists(id_lote):
            await db.disconnect()
            return None, ("lote_not_found", 404)

        # Construir filtro por rango de fechas
        where = {"id_lote": id_lote}
        if desde or hasta:
            fecha_filter = {}
            if desde:
                fecha_filter["gte"] = desde
            if hasta:
                fecha_filter["lte"] = hasta
            where["fecha_gasto"] = fecha_filter

        # Traer costos con su tipo (para conocer la categoria FIJO/VARIABLE)
        costos = await db.costo.find_many(
            where=where,
            include={"tipo_costo": True},
            order={"fecha_gasto": "asc"}
        )

        await db.disconnect()

        # Sumar por categoría
        total_fijo = 0.0
        total_variable = 0.0
        by_tipo = {}  # id_tipo_costo -> acumulador

        for c in costos:
            monto = float(c.monto or 0.0)
            categoria = (c.tipo_costo.categoria or "").upper()
            if categoria == "FIJO":
                total_fijo += monto
            elif categoria == "VARIABLE":
                total_variable += monto

            if with_detalle:
                key = c.id_tipo_costo
                if key not in by_tipo:
                    by_tipo[key] = {
                        "id_tipo_costo": c.id_tipo_costo,
                        "nombre_tipo": c.tipo_costo.nombre_tipo,
                        "categoria": categoria,
                        "total": 0.0,
                    }
                by_tipo[key]["total"] += monto

        payload = {
            "lote_id": id_lote,
            "period": {
                "desde": desde.isoformat() if desde else None,
                "hasta": hasta.isoformat() if hasta else None,
            },
            "totals": {
                "FIJO": round(total_fijo, 4),
                "VARIABLE": round(total_variable, 4),
                "TOTAL": round(total_fijo + total_variable, 4),
            },
        }

        if with_detalle:
            # Ordenar detalle por monto desc
            detalle_list = list(by_tipo.values())
            detalle_list.sort(key=lambda x: x["total"], reverse=True)
            # Redondear totales
            for d in detalle_list:
                d["total"] = round(d["total"], 4)
            payload["by_tipo"] = detalle_list

        return payload, None

    data, err = asyncio.run(_run())
    if err:
        msg, code = err
        if msg == "lote_not_found":
            return jsonify(error="Lote no encontrado"), code
        return jsonify(error=msg), code or 400

    return jsonify(data), 200
