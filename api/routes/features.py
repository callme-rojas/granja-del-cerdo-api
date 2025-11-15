# api/routes/features.py
from flask import Blueprint, jsonify, request
from utils.auth_guard import require_jwt
from services.features_service import build_features_para_modelo
from db import db
import asyncio

bp = Blueprint("features_v1", __name__)

# -----------------------------
# GET /lotes/<id>/features
# -----------------------------
@bp.get("/lotes/<int:id_lote>/features")
@require_jwt
def get_lote_features(id_lote: int):
    """
    Obtiene las features (variables) y extras (fijos) para un lote.
    
    Query params:
    - desde: fecha inicial (opcional)
    - hasta: fecha final (opcional)
    - detalle: si incluir desglose por tipo de costo (true/false)
    """
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
    detalle = (request.args.get("detalle") or "").lower() in ("1", "true", "yes", "y")

    async def _run():
        await db.connect()
        try:
            bundle = await build_features_para_modelo(
                id_lote=id_lote,
                desde=desde,
                hasta=hasta,
                with_detalle=detalle,
            )
            return bundle, None
        except ValueError as e:
            error_msg = str(e)
            if error_msg == "lote_not_found":
                return None, ("lote_not_found", 404)
            return None, (error_msg, 400)
        finally:
            await db.disconnect()

    data, err = asyncio.run(_run())
    if err:
        msg, code = err
        if msg == "lote_not_found":
            return jsonify(error="Lote no encontrado"), code
        return jsonify(error=msg), code or 400

    return jsonify(data), 200
