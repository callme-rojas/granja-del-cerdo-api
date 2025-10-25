from flask import Blueprint, jsonify
from flask_pydantic import validate
from pydantic import BaseModel, Field
from datetime import datetime
from utils.auth_guard import require_jwt
from db import db
import asyncio

bp = Blueprint("produccion_v1", __name__)

# ---------------------------------------------------
# 📦 MODELOS
# ---------------------------------------------------
class ProduccionCreate(BaseModel):
    fecha_corte: str = Field(..., description="Fecha del fin del ciclo (ISO 8601)")
    kilos_vendidos: float = Field(gt=0, description="Cantidad total de kilos vendidos")
    precio_venta_kg: float = Field(gt=0, description="Precio promedio de venta por kilo")

class ProduccionUpdate(BaseModel):
    kilos_vendidos: float | None = Field(default=None, gt=0)
    precio_venta_kg: float | None = Field(default=None, gt=0)

# ---------------------------------------------------
# 🔹 Helper para parsear fechas ISO
# ---------------------------------------------------
def parse_iso_date(s: str) -> datetime:
    s = s.strip().removesuffix("Z")
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return datetime.strptime(s, "%Y-%m-%d")

# ---------------------------------------------------
# 🔹 POST /lotes/<id_lote>/produccion
# ---------------------------------------------------
@bp.post("/lotes/<int:id_lote>/produccion")
@require_jwt
@validate()
def crear_produccion(id_lote: int, body: ProduccionCreate):
    """
    Crea un registro de producción para un lote.
    Solo puede haber una producción por lote.
    
    Body:
    - fecha_corte: Fecha del fin del ciclo (ISO 8601)
    - kilos_vendidos: Cantidad total de kilos vendidos
    - precio_venta_kg: Precio promedio de venta por kilo
    """
    async def _crear():
        await db.connect()
        lote = await db.lote.find_unique(where={"id_lote": id_lote})
        if not lote:
            await db.disconnect()
            return None, "lote_not_found"

        existing = await db.produccion.find_unique(where={"id_lote": id_lote})
        if existing:
            await db.disconnect()
            return None, "produccion_exists"

        fecha = parse_iso_date(body.fecha_corte)

        prod = await db.produccion.create(
            data={
                "id_lote": id_lote,
                "fecha_corte": fecha,
                "kilos_vendidos": body.kilos_vendidos,
                "precio_venta_kg": body.precio_venta_kg,
            }
        )
        await db.disconnect()
        return prod.dict(), None

    result, err = asyncio.run(_crear())
    if err == "lote_not_found":
        return jsonify(error="Lote no encontrado"), 404
    if err == "produccion_exists":
        return jsonify(error="Ya existe producción para este lote"), 409
    return jsonify(result), 201

# ---------------------------------------------------
# 🔹 GET /lotes/<id_lote>/produccion
# ---------------------------------------------------
@bp.get("/lotes/<int:id_lote>/produccion")
@require_jwt
def get_produccion(id_lote: int):
    """
    Obtiene el registro de producción de un lote.
    """
    async def _get():
        await db.connect()
        prod = await db.produccion.find_unique(where={"id_lote": id_lote})
        await db.disconnect()
        if not prod:
            return None, "not_found"
        return prod.dict(), None

    result, err = asyncio.run(_get())
    if err == "not_found":
        return jsonify(error="Producción no encontrada"), 404
    return jsonify(result), 200

# ---------------------------------------------------
# 🔹 PATCH /lotes/<id_lote>/produccion
# ---------------------------------------------------
@bp.patch("/lotes/<int:id_lote>/produccion")
@require_jwt
@validate()
def update_produccion(id_lote: int, body: ProduccionUpdate):
    """
    Actualiza el registro de producción de un lote.
    
    Body (opcional):
    - kilos_vendidos: Cantidad total de kilos vendidos
    - precio_venta_kg: Precio promedio de venta por kilo
    """
    async def _update():
        await db.connect()
        prod = await db.produccion.find_unique(where={"id_lote": id_lote})
        if not prod:
            await db.disconnect()
            return None, "not_found"

        data = {}
        if body.kilos_vendidos is not None:
            data["kilos_vendidos"] = body.kilos_vendidos
        if body.precio_venta_kg is not None:
            data["precio_venta_kg"] = body.precio_venta_kg

        if not data:
            await db.disconnect()
            return None, "no_fields"

        updated = await db.produccion.update(where={"id_lote": id_lote}, data=data)
        await db.disconnect()
        return updated.dict(), None

    result, err = asyncio.run(_update())
    if err == "not_found":
        return jsonify(error="Producción no encontrada"), 404
    if err == "no_fields":
        return jsonify(error="No hay campos para actualizar"), 400
    return jsonify(result), 200
