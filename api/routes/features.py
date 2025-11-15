# api/routes/features.py
from flask import Blueprint, jsonify, request
from utils.auth_guard import require_jwt
from services.features_service import build_features_para_modelo
from db import connect_db, disconnect_db
import asyncio
import logging

bp = Blueprint("features_v1", __name__)
logger = logging.getLogger(__name__)

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
        await connect_db()
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
            logger.error(f"ValueError en get_lote_features para lote {id_lote}: {error_msg}")
            if error_msg == "lote_not_found":
                return None, ("lote_not_found", 404)
            return None, (error_msg, 400)
        except Exception as e:
            # Capturar cualquier otra excepción
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"Error en get_lote_features para lote {id_lote}: {e}")
            logger.error(error_trace)
            return None, (f"Error interno: {str(e)}", 500)
        finally:
            await disconnect_db()

    try:
        data, err = asyncio.run(_run())
        if err:
            msg, code = err
            logger.warning(f"Error en get_lote_features: {msg} (código {code})")
            if msg == "lote_not_found":
                return jsonify(error="Lote no encontrado"), code
            return jsonify(error=msg), code or 400

        if data is None:
            logger.error(f"Data es None para lote {id_lote}")
            return jsonify(error="No se pudo obtener información del lote"), 500

        return jsonify(data), 200
    except Exception as e:
        # Manejar errores en la ejecución de asyncio.run
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Error crítico en get_lote_features: {e}")
        logger.error(error_trace)
        return jsonify(error=f"Error crítico: {str(e)}"), 500
