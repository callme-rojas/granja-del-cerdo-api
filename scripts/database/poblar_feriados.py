"""
Script para poblar feriados de Bolivia 2026.
Estos datos se usan para las features #20 y #21 del modelo XGBoost.

IMPORTANTE: Ejecutar desde la raíz del proyecto:
    python scripts/database/poblar_feriados.py
"""
import sys
from pathlib import Path

# Agregar path del directorio api para importar db
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "api"))

import asyncio
from datetime import datetime
from db import db

# Feriados de Bolivia 2026
FERIADOS_2026 = [
    # Enero
    {"nombre": "Año Nuevo", "fecha": datetime(2026, 1, 1), "descripcion": "Feriado nacional"},
    {"nombre": "Día del Estado Plurinacional", "fecha": datetime(2026, 1, 22), "descripcion": "Feriado nacional"},
    
    # Febrero
    {"nombre": "Carnaval", "fecha": datetime(2026, 2, 14), "descripcion": "Feriado nacional - Alta demanda"},
    {"nombre": "Carnaval", "fecha": datetime(2026, 2, 15), "descripcion": "Feriado nacional - Alta demanda"},
    {"nombre": "Carnaval", "fecha": datetime(2026, 2, 16), "descripcion": "Feriado nacional - Alta demanda"},
    
    # Marzo - Abril (Semana Santa - fechas movibles)
    {"nombre": "Viernes Santo", "fecha": datetime(2026, 4, 3), "descripcion": "Feriado nacional"},
    
    # Mayo
    {"nombre": "Día del Trabajo", "fecha": datetime(2026, 5, 1), "descripcion": "Feriado nacional"},
    
    # Junio
    {"nombre": "Corpus Christi", "fecha": datetime(2026, 6, 4), "descripcion": "Feriado nacional"},
    {"nombre": "Año Nuevo Andino", "fecha": datetime(2026, 6, 21), "descripcion": "Feriado nacional"},
    
    # Agosto
    {"nombre": "Día de la Independencia", "fecha": datetime(2026, 8, 6), "descripcion": "Feriado nacional - Alta demanda"},
    
    # Noviembre
    {"nombre": "Día de Todos los Santos", "fecha": datetime(2026, 11, 2), "descripcion": "Feriado nacional"},
    
    # Diciembre
    {"nombre": "Navidad", "fecha": datetime(2026, 12, 25), "descripcion": "Feriado nacional - Alta demanda"},
    {"nombre": "Fin de Año", "fecha": datetime(2026, 12, 31), "descripcion": "Celebración - Alta demanda"},
]


async def poblar_feriados():
    """
    Pobla la tabla Feriado con los feriados de Bolivia 2026.
    """
    await db.connect()
    
    try:
        print("🎉 Poblando feriados de Bolivia 2026...")
        
        feriados_creados = 0
        feriados_existentes = 0
        
        for feriado_data in FERIADOS_2026:
            try:
                # Verificar si ya existe
                existe = await db.feriado.find_first(
                    where={
                        "fecha": feriado_data["fecha"],
                        "nombre_feriado": feriado_data["nombre"]
                    }
                )
                
                if existe:
                    feriados_existentes += 1
                    print(f"⚠️  Ya existe: {feriado_data['nombre']} - {feriado_data['fecha'].strftime('%d/%m/%Y')}")
                else:
                    feriado = await db.feriado.create(
                        data={
                            "nombre_feriado": feriado_data["nombre"],
                            "fecha": feriado_data["fecha"],
                            "descripcion": feriado_data["descripcion"]
                        }
                    )
                    feriados_creados += 1
                    print(f"✅ Creado: {feriado.nombre_feriado} - {feriado.fecha.strftime('%d/%m/%Y')}")
                    
            except Exception as e:
                print(f"❌ Error al crear {feriado_data['nombre']}: {str(e)}")
        
        print(f"\n📊 Resumen:")
        print(f"   Feriados creados: {feriados_creados}")
        print(f"   Feriados ya existentes: {feriados_existentes}")
        print(f"   Total en BD: {await db.feriado.count()}")
        
    finally:
        await db.disconnect()


async def verificar_feriado_proximo(fecha_lote: datetime):
    """
    Ejemplo de cómo calcular las features #20 y #21.
    
    Args:
        fecha_lote: Fecha de adquisición del lote
        
    Returns:
        tuple: (es_feriado_proximo, dias_para_festividad)
    """
    await db.connect()
    
    try:
        from datetime import timedelta
        
        # Buscar feriados en los próximos 7 días
        fecha_limite = fecha_lote + timedelta(days=7)
        
        feriados_proximos = await db.feriado.find_many(
            where={
                "fecha": {
                    "gte": fecha_lote,
                    "lte": fecha_limite
                }
            },
            order={"fecha": "asc"}
        )
        
        if feriados_proximos:
            feriado_mas_cercano = feriados_proximos[0]
            dias_para_festividad = (feriado_mas_cercano.fecha - fecha_lote).days
            es_feriado_proximo = True
            
            print(f"\n🎉 Feriado próximo detectado:")
            print(f"   Nombre: {feriado_mas_cercano.nombre_feriado}")
            print(f"   Fecha: {feriado_mas_cercano.fecha.strftime('%d/%m/%Y')}")
            print(f"   Días para festividad: {dias_para_festividad}")
        else:
            es_feriado_proximo = False
            dias_para_festividad = 999  # Sin festividad próxima
            print(f"\n📅 No hay feriados en los próximos 7 días")
        
        return es_feriado_proximo, dias_para_festividad
        
    finally:
        await db.disconnect()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "verificar":
        # Ejemplo: python scripts/database/poblar_feriados.py verificar 2026-02-10
        if len(sys.argv) < 3:
            print("Uso: python scripts/database/poblar_feriados.py verificar YYYY-MM-DD")
        else:
            fecha_str = sys.argv[2]
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
            asyncio.run(verificar_feriado_proximo(fecha))
    else:
        asyncio.run(poblar_feriados())
