"""
Script de Reporte de Base de Datos
Muestra un resumen del estado actual de la base de datos
"""
import asyncio
from db import db
from datetime import datetime
import pandas as pd

async def revisar_datos():
    with open("reporte_bd.txt", "w", encoding="utf-8") as f:
        def log(msg):
            print(msg)
            f.write(msg + "\\n")
            
        log("📊 INSPECCIÓN DE BASE DE DATOS")
        log("=" * 50)
    
        await db.connect()
    
        try:
            # 1. Conteos Generales
            log("\\n1️⃣  RESUMEN DE REGISTROS")
            log("-" * 30)
            conteos = {
                "Lotes": await db.lote.count(),
                "Tipos de Costo": await db.tipocosto.count(),
                "Costos Registrados": await db.costo.count(),
                "Gastos Mensuales": await db.gastomensual.count(),
                "Feriados": await db.feriado.count(),
                "Producciones": await db.produccion.count(),
                "Predicciones": await db.prediccion.count()
            }
            
            for k, v in conteos.items():
                log(f"{k.ljust(20)}: {v}")

            # 2. Análisis de Lotes
            log("\\n2️⃣  ANÁLISIS DE LOTES (Últimos 5)")
            log("-" * 30)
            lotes = await db.lote.find_many(
                take=5,
                order={"fecha_adquisicion": "desc"},
                include={"costos": True, "produccion": True}
            )
            
            if lotes:
                log(f"{'ID':<5} {'Fecha':<12} {'Animales':<10} {'Peso Ent.':<10} {'Costos':<8} {'Prod?':<6}")
                log("-" * 60)
                for lote in lotes:
                    tiene_prod = "Sí" if lote.produccion else "No"
                    num_costos = len(lote.costos)
                    fecha = lote.fecha_adquisicion.strftime("%Y-%m-%d")
                    log(f"{lote.id_lote:<5} {fecha:<12} {lote.cantidad_animales:<10} {lote.peso_promedio_entrada:<10} {num_costos:<8} {tiene_prod:<6}")
            else:
                log("⚠️ No hay lotes registrados")

            # 3. Tipos de Costo
            log("\\n3️⃣  TIPOS DE COSTO DISPONIBLES")
            log("-" * 30)
            tipos = await db.tipocosto.find_many()
            for t in tipos:
                log(f"- {t.nombre_tipo} ({t.categoria})")

            # 4. Verificación de Integridad
            log("\\n4️⃣  VERIFICACIÓN DE INTEGRIDAD")
            log("-" * 30)
            
            # Lotes sin costos
            lotes_sin_costos = await db.lote.count(where={"costos": {"none": {}}})
            if lotes_sin_costos > 0:
                log(f"⚠️ Alerta: Hay {lotes_sin_costos} lotes sin costos registrados")
            else:
                log("✅ Todos los lotes tienen costos asociados")
                
            log("\\n" + "=" * 50)

        except Exception as e:
            log(f"❌ Error al leer la base de datos: {e}")
        finally:
            await db.disconnect()

if __name__ == "__main__":
    asyncio.run(revisar_datos())
