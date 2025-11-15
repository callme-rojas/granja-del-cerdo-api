from flask import Blueprint, jsonify
from flask_pydantic import validate
from pydantic import BaseModel, Field
from utils.auth_guard import require_jwt
from db import db
import asyncio

bp = Blueprint("tipos_costo_v1", __name__)

class TipoCostoCreate(BaseModel):
    nombre_tipo: str = Field(min_length=3, max_length=80)
    categoria: str = Field(pattern="^(FIJO|VARIABLE)$")  # Enum del Prisma


class TipoCostoUpdate(BaseModel):
    nombre_tipo: str = Field(min_length=3, max_length=80)


class TipoCostoUpdateCategoria(BaseModel):
    categoria: str = Field(pattern="^(FIJO|VARIABLE)$")

# -------------------------
# GET /tipos-costo
# -------------------------
@bp.get("/tipos-costo")
@require_jwt
def listar_tipos_costo():
    async def _listar_tipos():
        await db.connect()
        tipos = await db.tipocosto.find_many(order={"id_tipo_costo": "asc"})
        await db.disconnect()
        return [t.dict() for t in tipos]
    
    tipos = asyncio.run(_listar_tipos())
    return jsonify(tipos), 200


# -------------------------
# POST /tipos-costo
# -------------------------
@bp.post("/tipos-costo")
@require_jwt
@validate()
def crear_tipo_costo(body: TipoCostoCreate):
    async def _crear_tipo():
        await db.connect()
        # Evitar duplicados por nombre
        exists = await db.tipocosto.find_first(
            where={"nombre_tipo": {"equals": body.nombre_tipo, "mode": "insensitive"}}
        )
        if exists:
            await db.disconnect()
            return None, "tipo_costo_exists"

        tipo = await db.tipocosto.create(
            data={
                "nombre_tipo": body.nombre_tipo,
                "categoria": body.categoria
            }
        )
        await db.disconnect()
        return tipo.dict(), None
    
    tipo_data, error = asyncio.run(_crear_tipo())
    if error:
        if error == "tipo_costo_exists":
            return jsonify(error="El tipo de costo ya existe"), 409
        return jsonify(error=error), 400
    
    return jsonify(tipo_data), 201

# -------------------------
# PATCH /tipos-costo/<id>
# Actualiza solo el nombre
# -------------------------
@bp.patch("/tipos-costo/<int:id_tipo_costo>")
@require_jwt
@validate()
def actualizar_tipo_costo(id_tipo_costo: int, body: TipoCostoUpdate):
    async def _actualizar_tipo():
        await db.connect()
        
        # Verificar si existe
        tipo_existente = await db.tipocosto.find_unique(where={"id_tipo_costo": id_tipo_costo})
        if not tipo_existente:
            await db.disconnect()
            return None, "tipo_costo_not_found"
        
        # Verificar duplicado de nombre
        exists = await db.tipocosto.find_first(
            where={
                "nombre_tipo": {"equals": body.nombre_tipo, "mode": "insensitive"},
                "id_tipo_costo": {"not": id_tipo_costo}
            }
        )
        if exists:
            await db.disconnect()
            return None, "tipo_costo_exists"
        
        # Actualizar
        tipo = await db.tipocosto.update(
            where={"id_tipo_costo": id_tipo_costo},
            data={"nombre_tipo": body.nombre_tipo}
        )
        await db.disconnect()
        return tipo.dict(), None
    
    tipo_data, error = asyncio.run(_actualizar_tipo())
    if error:
        if error == "tipo_costo_not_found":
            return jsonify(error="Tipo de costo no encontrado"), 404
        elif error == "tipo_costo_exists":
            return jsonify(error="El nombre del tipo de costo ya existe"), 409
        return jsonify(error=error), 400
    
    return jsonify(tipo_data), 200


# -------------------------
# PATCH /tipos-costo/<id>/categoria
# Actualiza solo la categoría (FIJO/VARIABLE)
# -------------------------
@bp.patch("/tipos-costo/<int:id_tipo_costo>/categoria")
@require_jwt
@validate()
def actualizar_categoria_tipo_costo(id_tipo_costo: int, body: TipoCostoUpdateCategoria):
    async def _actualizar_cat():
        await db.connect()
        tipo = await db.tipocosto.find_unique(where={"id_tipo_costo": id_tipo_costo})
        if not tipo:
            await db.disconnect()
            return None, "tipo_costo_not_found"

        tipo = await db.tipocosto.update(
            where={"id_tipo_costo": id_tipo_costo},
            data={"categoria": body.categoria}
        )
        await db.disconnect()
        return tipo.dict(), None

    result, error = asyncio.run(_actualizar_cat())
    if error:
        return jsonify(error="Tipo de costo no encontrado"), 404
    return jsonify(result), 200
# -------------------------
# DELETE /tipos-costo/<id>
# -------------------------
@bp.delete("/tipos-costo/<int:id_tipo_costo>")
@require_jwt
def eliminar_tipo_costo(id_tipo_costo: int):
    async def _eliminar_tipo():
        await db.connect()
        
        tipo_existente = await db.tipocosto.find_unique(where={"id_tipo_costo": id_tipo_costo})
        if not tipo_existente:
            await db.disconnect()
            return None, "tipo_costo_not_found"
        
        # Validar relaciones
        costos_asociados = await db.costo.find_first(where={"id_tipo_costo": id_tipo_costo})
        if costos_asociados:
            await db.disconnect()
            return None, "tipo_costo_has_costs"
        
        await db.tipocosto.delete(where={"id_tipo_costo": id_tipo_costo})
        await db.disconnect()
        return {"message": f"Tipo de costo {id_tipo_costo} eliminado"}, None
    
    result, error = asyncio.run(_eliminar_tipo())
    if error:
        if error == "tipo_costo_not_found":
            return jsonify(error="Tipo de costo no encontrado"), 404
        elif error == "tipo_costo_has_costs":
            return jsonify(error="No se puede eliminar: hay costos asociados a este tipo"), 409
        return jsonify(error=error), 400
    
    return jsonify(result), 200
