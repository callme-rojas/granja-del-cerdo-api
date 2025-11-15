from flask import Blueprint, jsonify, request
from flask_pydantic import validate
from pydantic import BaseModel, Field
from utils.auth_guard import require_jwt
from db import db, connect_db, disconnect_db
import re
import asyncio
from datetime import datetime


bp = Blueprint("lotes_v1", __name__)

class LoteCreate(BaseModel):
    fecha_adquisicion: str  # ISO string: "YYYY-MM-DD" o "YYYY-MM-DDTHH:MM:SS"
    cantidad_animales: int = Field(gt=0)
    peso_promedio_entrada: float = Field(gt=0)
    duracion_estadia_dias: int | None = Field(default=None, ge=0, le=7)  
    precio_compra_kg: float | None = Field(default=None, gt=0)  

@bp.post("/lotes")
@require_jwt
@validate()
def create_lote(body: LoteCreate):
    async def _create_lote():
        payload = getattr(request, "user", {})
        id_usuario = payload.get("uid")

        fecha_str = body.fecha_adquisicion
        print(f"🧭 Valor recibido en fecha_adquisicion: {fecha_str}")

        # Intentar parsear fecha en distintos formatos
        fecha = None
        try:
            # ISO completo con Z o sin Z
            clean_str = re.sub(r"Z$", "", fecha_str.strip())
            fecha = datetime.fromisoformat(clean_str)
        except Exception:
            try:
                # Formato solo fecha (YYYY-MM-DD)
                fecha = datetime.strptime(fecha_str.strip(), "%Y-%m-%d")
            except Exception as e:
                print(f"⚠️ Error al convertir fecha: {e}")
                return None, "invalid_fecha_adquisicion_format"

        await connect_db()
        try:
            lote = await db.lote.create(
                data={
                    "fecha_adquisicion": fecha,
                    "cantidad_animales": body.cantidad_animales,
                    "peso_promedio_entrada": body.peso_promedio_entrada,
                    "duracion_estadia_dias": body.duracion_estadia_dias,  
                    "precio_compra_kg": body.precio_compra_kg,
                    "id_usuario_creador": id_usuario,
                }
            )
            return lote.dict(), None
        finally:
            await disconnect_db()
    
    lote_data, error = asyncio.run(_create_lote())
    if error:
        return jsonify(error=error), 400
    return jsonify(lote_data), 201
    
@bp.get("/lotes")
@require_jwt
def get_lotes():
    async def _get_lotes():
        await connect_db()
        try:
            lotes = await db.lote.find_many(order={"id_lote": "desc"})
            return [lote.dict() for lote in lotes]
        finally:
            await disconnect_db()
    
    lotes = asyncio.run(_get_lotes())
    return jsonify(lotes), 200
    
class LoteUpdate(BaseModel):
    # Campos que se pueden actualizar en un lote
    fecha_adquisicion: str | None = Field(default=None, description="Fecha de adquisición en formato ISO")
    cantidad_animales: int | None = Field(default=None, gt=0, description="Cantidad de animales")
    peso_promedio_entrada: float | None = Field(default=None, gt=0, description="Peso promedio de entrada")
    duracion_estadia_dias: int | None = Field(default=None, ge=0, le=7, description="Duración de estadía en días (0-7)")
    precio_compra_kg: float | None = Field(default=None, gt=0, description="Precio de compra por kg")

@bp.patch("/lotes/<int:id_lote>")
@require_jwt
@validate()
def update_lote(id_lote: int, body: LoteUpdate):
    async def _update_lote():
        # Preparar datos para actualización
        update_data = {}
        
        # Procesar cada campo si está presente
        if body.fecha_adquisicion is not None:
            fecha_str = body.fecha_adquisicion
            print(f"🧭 Actualizando fecha_adquisicion: {fecha_str}")
            
            # Intentar parsear fecha en distintos formatos
            fecha = None
            try:
                # ISO completo con Z o sin Z
                clean_str = re.sub(r"Z$", "", fecha_str.strip())
                fecha = datetime.fromisoformat(clean_str)
            except Exception:
                try:
                    # Formato solo fecha (YYYY-MM-DD)
                    fecha = datetime.strptime(fecha_str.strip(), "%Y-%m-%d")
                except Exception as e:
                    print(f"⚠️ Error al convertir fecha: {e}")
                    return None, "invalid_fecha_adquisicion_format"
            
            update_data["fecha_adquisicion"] = fecha
        
        if body.cantidad_animales is not None:
            update_data["cantidad_animales"] = body.cantidad_animales
        
        if body.peso_promedio_entrada is not None:
            update_data["peso_promedio_entrada"] = body.peso_promedio_entrada
        
        if body.duracion_estadia_dias is not None:
            update_data["duracion_estadia_dias"] = body.duracion_estadia_dias
        
        if body.precio_compra_kg is not None:
            update_data["precio_compra_kg"] = body.precio_compra_kg
        
        # Si no hay datos para actualizar
        if not update_data:
            return None, "no_fields_to_update"
        
        await connect_db()
        try:
            lote = await db.lote.update(where={"id_lote": id_lote}, data=update_data)
            return lote.dict(), None
        finally:
            await disconnect_db()
    
    lote_data, error = asyncio.run(_update_lote())
    if error:
        if error == "no_fields_to_update":
            return jsonify(error="No hay campos para actualizar"), 400
        elif error == "invalid_fecha_adquisicion_format":
            return jsonify(error="Formato de fecha inválido"), 400
        else:
            return jsonify(error=error), 400
    
    return jsonify(lote_data)

@bp.delete("/lotes/<int:id_lote>")
@require_jwt
def delete_lote(id_lote: int):
    async def _delete_lote():
        await connect_db()
        try:
            await db.lote.delete(where={"id_lote": id_lote})
            return {"message": f"Lote {id_lote} eliminado"}
        finally:
            await disconnect_db()
    
    result = asyncio.run(_delete_lote())
    return jsonify(result)
