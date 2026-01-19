"""
Script para analizar valores nulos en la tabla Lote
"""
import asyncio
from db import db

async def analizar_nulos():
    print("🔍 ANÁLISIS DE VALORES NULOS EN LOTES")
    print("=" * 50)
    
    await db.connect()
    
    try:
        total_lotes = await db.lote.count()
        print(f"Total de Lotes: {total_lotes}\n")
        
        campos_a_verificar = [
            "duracion_estadia_dias",
            "precio_compra_kg",
            "costo_flete",
            "costo_combustible",
            "costo_peajes_lavado",
            "merma_peso_transporte",
            "ubicacion_origen"
        ]
        
        print(f"{'Campo':<25} {'Nulos':<10} {'% Nulos'}")
        print("-" * 50)
        
        for campo in campos_a_verificar:
            # Contar nulos dinámicamente
            query = {campo: None}
            nulos = await db.lote.count(where=query)
            porcentaje = (nulos / total_lotes) * 100
            print(f"{campo:<25} {nulos:<10} {porcentaje:.1f}%")

        # Verificar Producción (Relación 1:1)
        lotes_sin_prod = await db.lote.count(where={"produccion": {"is": None}})
        porc_sin_prod = (lotes_sin_prod / total_lotes) * 100
        print(f"{'produccion (relación)':<25} {lotes_sin_prod:<10} {porc_sin_prod:.1f}%")
        
        print("\n" + "=" * 50)

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(analizar_nulos())
