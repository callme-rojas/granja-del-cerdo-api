"""
Script de ejemplo para poblar gastos mensuales en la base de datos.
Útil para testing y demostración del prorrateo de costos indirectos.

IMPORTANTE: Ejecutar desde la raíz del proyecto:
    python scripts/database/poblar_gastos_mensuales.py
"""
import sys
from pathlib import Path

# Agregar path del directorio api para importar db
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "api"))

import asyncio
from datetime import datetime
from db import db

async def poblar_gastos_mensuales_ejemplo():
    """
    Crea gastos mensuales de ejemplo para enero y febrero 2026.
    """
    await db.connect()
    
    try:
        print("🔧 Poblando gastos mensuales de ejemplo...")
        
        # Obtener o crear tipos de costo FIJO
        tipo_luz = await db.tipocosto.find_first(where={"nombre_tipo": "Servicios Basicos"})
        if not tipo_luz:
            tipo_luz = await db.tipocosto.create(data={
                "nombre_tipo": "Servicios Basicos",
                "categoria": "FIJO"
            })
            print("✅ Tipo de costo 'Servicios Basicos' creado")
        
        tipo_sueldo = await db.tipocosto.find_first(where={"nombre_tipo": "Mano de Obra Administrativa"})
        if not tipo_sueldo:
            tipo_sueldo = await db.tipocosto.create(data={
                "nombre_tipo": "Mano de Obra Administrativa",
                "categoria": "FIJO"
            })
            print("✅ Tipo de costo 'Mano de Obra Administrativa' creado")
        
        tipo_mantenimiento = await db.tipocosto.find_first(where={"nombre_tipo": "Mantenimiento de Instalaciones"})
        if not tipo_mantenimiento:
            tipo_mantenimiento = await db.tipocosto.create(data={
                "nombre_tipo": "Mantenimiento de Instalaciones",
                "categoria": "FIJO"
            })
            print("✅ Tipo de costo 'Mantenimiento de Instalaciones' creado")

        
        # Gastos de Enero 2026
        gastos_enero = [
            {
                "mes": 1,
                "anio": 2026,
                "monto": 850.0,
                "descripcion": "Luz eléctrica - Enero",
                "id_tipo_costo": tipo_luz.id_tipo_costo
            },
            {
                "mes": 1,
                "anio": 2026,
                "monto": 12000.0,
                "descripcion": "Sueldos administrativos - Enero",
                "id_tipo_costo": tipo_sueldo.id_tipo_costo
            },
            {
                "mes": 1,
                "anio": 2026,
                "monto": 1500.0,
                "descripcion": "Mantenimiento de corrales - Enero",
                "id_tipo_costo": tipo_mantenimiento.id_tipo_costo
            },
        ]
        
        # Gastos de Febrero 2026
        gastos_febrero = [
            {
                "mes": 2,
                "anio": 2026,
                "monto": 920.0,
                "descripcion": "Luz eléctrica - Febrero",
                "id_tipo_costo": tipo_luz.id_tipo_costo
            },
            {
                "mes": 2,
                "anio": 2026,
                "monto": 12000.0,
                "descripcion": "Sueldos administrativos - Febrero",
                "id_tipo_costo": tipo_sueldo.id_tipo_costo
            },
            {
                "mes": 2,
                "anio": 2026,
                "monto": 800.0,
                "descripcion": "Reparación de bebederos - Febrero",
                "id_tipo_costo": tipo_mantenimiento.id_tipo_costo
            },
        ]
        
        # Crear gastos
        for gasto_data in gastos_enero + gastos_febrero:
            try:
                gasto = await db.gastomensual.create(data=gasto_data)
                print(f"✅ Gasto creado: {gasto.descripcion} - Bs {gasto.monto}")
            except Exception as e:
                print(f"⚠️ Gasto ya existe o error: {gasto_data['descripcion']}")
        
        print("\n✅ Gastos mensuales poblados exitosamente")
        
        # Mostrar resumen
        total_gastos = await db.gastomensual.count()
        print(f"\n📊 Total de gastos mensuales en BD: {total_gastos}")
        
    finally:
        await db.disconnect()


async def calcular_prorrateo_ejemplo(id_lote: int):
    """
    Ejemplo de cómo calcular el prorrateo de gastos mensuales para un lote.
    """
    await db.connect()
    
    try:
        # Obtener lote
        lote = await db.lote.find_unique(where={"id_lote": id_lote})
        
        if not lote:
            print(f"❌ Lote {id_lote} no encontrado")
            return
        
        # Obtener mes y año del lote
        mes = lote.fecha_adquisicion.month
        anio = lote.fecha_adquisicion.year
        
        print(f"\n🔍 Calculando prorrateo para Lote #{id_lote}")
        print(f"   Fecha adquisición: {lote.fecha_adquisicion.strftime('%d/%m/%Y')}")
        print(f"   Cantidad animales: {lote.cantidad_animales}")
        
        # Obtener gastos del mes
        gastos_mes = await db.gastomensual.find_many(
            where={"mes": mes, "anio": anio},
            include={"tipo_costo": True}
        )
        
        if not gastos_mes:
            print(f"⚠️ No hay gastos mensuales registrados para {mes}/{anio}")
            return
        
        print(f"\n📋 Gastos mensuales de {mes}/{anio}:")
        for gasto in gastos_mes:
            print(f"   - {gasto.tipo_costo.nombre_tipo}: Bs {gasto.monto}")
        
        # Obtener todos los lotes del mes
        from datetime import datetime
        inicio_mes = datetime(anio, mes, 1)
        if mes == 12:
            fin_mes = datetime(anio + 1, 1, 1)
        else:
            fin_mes = datetime(anio, mes + 1, 1)
        
        lotes_del_mes = await db.lote.find_many(
            where={
                "fecha_adquisicion": {
                    "gte": inicio_mes,
                    "lt": fin_mes
                }
            }
        )
        
        total_animales_mes = sum(l.cantidad_animales for l in lotes_del_mes)
        
        print(f"\n📊 Total de animales vendidos en {mes}/{anio}: {total_animales_mes}")
        print(f"   Lotes en el mes: {len(lotes_del_mes)}")
        
        # Calcular prorrateo
        gasto_total_mes = sum(g.monto for g in gastos_mes)
        proporcion = lote.cantidad_animales / total_animales_mes
        gasto_prorrateado = gasto_total_mes * proporcion
        
        print(f"\n💰 Cálculo de Prorrateo:")
        print(f"   Gasto total del mes: Bs {gasto_total_mes:.2f}")
        print(f"   Proporción del lote: {proporcion:.4f} ({proporcion*100:.2f}%)")
        print(f"   Gasto prorrateado: Bs {gasto_prorrateado:.2f}")
        print(f"   Gasto por animal: Bs {gasto_prorrateado/lote.cantidad_animales:.2f}")
        
        return gasto_prorrateado
        
    finally:
        await db.disconnect()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "calcular":
        if len(sys.argv) < 3:
            print("Uso: python scripts/database/poblar_gastos_mensuales.py calcular <id_lote>")
        else:
            id_lote = int(sys.argv[2])
            asyncio.run(calcular_prorrateo_ejemplo(id_lote))
    else:
        asyncio.run(poblar_gastos_mensuales_ejemplo())
