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
    peso_salida_total: float = Field(gt=0, description="Cantidad total de kilos vendidos")
    mortalidad_unidades: int | None = Field(default=None, ge=0, description="Unidades de cerdos muertos")

class ProduccionUpdate(BaseModel):
    peso_salida_total: float | None = Field(default=None, gt=0)
    mortalidad_unidades: int | None = Field(default=None, ge=0)

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
    - peso_salida_total: Cantidad total de kilos vendidos
    - mortalidad_unidades: Número de cerdos muertos (opcional)
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

        prod = await db.produccion.create(
            data={
                "id_lote": id_lote,
                "peso_salida_total": body.peso_salida_total,
                "mortalidad_unidades": body.mortalidad_unidades,
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
    - peso_salida_total: Cantidad total de kilos vendidos
    - mortalidad_unidades: Número de cerdos muertos
    """
    async def _update():
        await db.connect()
        prod = await db.produccion.find_unique(where={"id_lote": id_lote})
        if not prod:
            await db.disconnect()
            return None, "not_found"

        data = {}
        if body.peso_salida_total is not None:
            data["peso_salida_total"] = body.peso_salida_total
        if body.mortalidad_unidades is not None:
            data["mortalidad_unidades"] = body.mortalidad_unidades

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
