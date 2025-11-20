from flask import Blueprint, jsonify, request
from flask_pydantic import validate
from pydantic import BaseModel, Field
from datetime import datetime
from utils.auth_guard import require_jwt
from db import db
import asyncio

bp = Blueprint("costos_v1", __name__)

def parse_iso(dt: str) -> datetime:
    """
    Parsea una fecha ISO y la devuelve con hora 00:00:00 (solo fecha).
    """
    s = dt.strip().removesuffix("Z")
    try:
        fecha = datetime.fromisoformat(s)
    except Exception:
        fecha = datetime.strptime(s, "%Y-%m-%d")
    # Asegurar que la hora sea 00:00:00 (solo fecha)
    return fecha.replace(hour=0, minute=0, second=0, microsecond=0)

async def ensure_lote_exists(id_lote: int) -> bool:
    return await db.lote.find_unique(where={"id_lote": id_lote}) is not None

async def ensure_tipocosto_exists(id_tipo_costo: int) -> bool:
    return await db.tipocosto.find_unique(where={"id_tipo_costo": id_tipo_costo}) is not None

class CostoCreate(BaseModel):
    monto: float = Field(gt=0)
    fecha_gasto: str
    id_tipo_costo: int = Field(gt=0)
    descripcion: str | None = Field(default=None, max_length=200)

class CostoUpdate(BaseModel):
    monto: float | None = Field(default=None, gt=0)
    fecha_gasto: str | None = Field(default=None)
    id_tipo_costo: int | None = Field(default=None, gt=0)
    descripcion: str | None = Field(default=None, max_length=200)

@bp.get("/lotes/<int:id_lote>/costos")
@require_jwt
def listar_costos(id_lote: int):
    async def _listar_costos():
        await db.connect()
        if not await ensure_lote_exists(id_lote):
            await db.disconnect()
            return None, "lote_not_found"

        where = {"id_lote": id_lote}
        tipo = request.args.get("tipo")
        if tipo and tipo.isdigit():
            where["id_tipo_costo"] = int(tipo)

        desde = request.args.get("desde")
        hasta = request.args.get("hasta")
        if desde or hasta:
            where["fecha_gasto"] = {}
            if desde:
                where["fecha_gasto"]["gte"] = parse_iso(desde)
            if hasta:
                where["fecha_gasto"]["lte"] = parse_iso(hasta)

        costos = await db.costo.find_many(
            where=where,
            order={"fecha_gasto": "desc"},
            include={"tipo_costo": True},
        )
        await db.disconnect()
        return [c.dict() for c in costos], None
    
    costos_data, error = asyncio.run(_listar_costos())
    if error:
        if error == "lote_not_found":
            return jsonify(error="Lote no encontrado"), 404
        return jsonify(error=error), 400
    
    return jsonify(costos_data), 200

@bp.post("/lotes/<int:id_lote>/costos")
@require_jwt
@validate()
def crear_costo(id_lote: int, body: CostoCreate):
    async def _crear_costo():
        await db.connect()
        if not await ensure_lote_exists(id_lote):
            await db.disconnect()
            return None, "lote_not_found"
        if not await ensure_tipocosto_exists(body.id_tipo_costo):
            await db.disconnect()
            return None, "tipo_costo_not_found"

        costo = await db.costo.create(
            data={
                "id_lote": id_lote,
                "monto": body.monto,
                "fecha_gasto": parse_iso(body.fecha_gasto),
                "descripcion": body.descripcion,
                "id_tipo_costo": body.id_tipo_costo,
            },
            include={"tipo_costo": True},
        )
        await db.disconnect()
        return costo.dict(), None
    
    costo_data, error = asyncio.run(_crear_costo())
    if error:
        if error == "lote_not_found":
            return jsonify(error="Lote no encontrado"), 404
        elif error == "tipo_costo_not_found":
            return jsonify(error="Tipo de costo no encontrado"), 404
        return jsonify(error=error), 400
    
    return jsonify(costo_data), 201

@bp.patch("/lotes/<int:id_lote>/costos/<int:id_costo>")
@require_jwt
@validate()
def actualizar_costo(id_lote: int, id_costo: int, body: CostoUpdate):
    async def _actualizar_costo():
        await db.connect()
        
        # Verificar si el costo existe y pertenece al lote
        costo_existente = await db.costo.find_first(
            where={"id_costo": id_costo, "id_lote": id_lote}
        )
        if not costo_existente:
            await db.disconnect()
            return None, "costo_not_found"
        
        # Preparar datos para actualización
        update_data = {}
        
        if body.monto is not None:
            update_data["monto"] = body.monto
        
        if body.fecha_gasto is not None:
            update_data["fecha_gasto"] = parse_iso(body.fecha_gasto)
        
        if body.id_tipo_costo is not None:
            # Verificar que el tipo de costo existe
            if not await ensure_tipocosto_exists(body.id_tipo_costo):
                await db.disconnect()
                return None, "tipo_costo_not_found"
            update_data["id_tipo_costo"] = body.id_tipo_costo
        
        if body.descripcion is not None:
            update_data["descripcion"] = body.descripcion
        
        # Si no hay datos para actualizar
        if not update_data:
            await db.disconnect()
            return None, "no_fields_to_update"
        
        # Actualizar el costo
        costo = await db.costo.update(
            where={"id_costo": id_costo},
            data=update_data,
            include={"tipo_costo": True}
        )
        await db.disconnect()
        return costo.dict(), None
    
    costo_data, error = asyncio.run(_actualizar_costo())
    if error:
        if error == "costo_not_found":
            return jsonify(error="Costo no encontrado"), 404
        elif error == "tipo_costo_not_found":
            return jsonify(error="Tipo de costo no encontrado"), 404
        elif error == "no_fields_to_update":
            return jsonify(error="No hay campos para actualizar"), 400
        return jsonify(error=error), 400
    
    return jsonify(costo_data)

@bp.delete("/lotes/<int:id_lote>/costos/<int:id_costo>")
@require_jwt
def eliminar_costo(id_lote: int, id_costo: int):
    async def _eliminar_costo():
        await db.connect()
        
        # Verificar si el costo existe y pertenece al lote
        costo_existente = await db.costo.find_first(
            where={"id_costo": id_costo, "id_lote": id_lote}
        )
        if not costo_existente:
            await db.disconnect()
            return None, "costo_not_found"
        
        # Eliminar el costo
        await db.costo.delete(where={"id_costo": id_costo})
        await db.disconnect()
        return {"message": f"Costo {id_costo} eliminado del lote {id_lote}"}, None
    
    result, error = asyncio.run(_eliminar_costo())
    if error:
        if error == "costo_not_found":
            return jsonify(error="Costo no encontrado"), 404
        return jsonify(error=error), 400
    
    return jsonify(result)
