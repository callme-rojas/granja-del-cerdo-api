#!/usr/bin/env python3
"""
Script para poblar la tabla TipoCosto con tipos de costo básicos.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Agregar el directorio api al path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# Cargar variables de entorno
env_path = script_dir / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"[OK] Variables de entorno cargadas desde: {env_path}")
else:
    # Intentar desde el root del proyecto
    root_env = script_dir.parent / ".env"
    if root_env.exists():
        load_dotenv(root_env)
        print(f"[OK] Variables de entorno cargadas desde: {root_env}")
    else:
        load_dotenv()
        print("[WARNING] No se encontró archivo .env, usando variables del sistema")

# Verificar DATABASE_URL
if not os.getenv("DATABASE_URL"):
    print("[ERROR] DATABASE_URL no encontrada en variables de entorno")
    print("   Por favor, verifica que el archivo .env contenga DATABASE_URL")
    sys.exit(1)

# Importar db después de cargar las variables de entorno
from db import db
import asyncio

# Tipos de costo a insertar
TIPOS_COSTO = [
    # Costos VARIABLES (dependen de la cantidad de animales o producción)
    {"nombre_tipo": "Alimentación", "categoria": "VARIABLE"},
    {"nombre_tipo": "Logística", "categoria": "VARIABLE"},
    {"nombre_tipo": "Veterinario", "categoria": "VARIABLE"},
    {"nombre_tipo": "Medicamentos", "categoria": "VARIABLE"},
    {"nombre_tipo": "Vacunas", "categoria": "VARIABLE"},
    {"nombre_tipo": "Transporte", "categoria": "VARIABLE"},
    {"nombre_tipo": "Mano de obra directa", "categoria": "VARIABLE"},
    {"nombre_tipo": "Agua", "categoria": "VARIABLE"},
    {"nombre_tipo": "Energía eléctrica", "categoria": "VARIABLE"},
    {"nombre_tipo": "Materiales de limpieza", "categoria": "VARIABLE"},
    
    # Costos FIJOS (no dependen directamente de la cantidad de animales)
    {"nombre_tipo": "Alquiler de instalaciones", "categoria": "FIJO"},
    {"nombre_tipo": "Mano de obra administrativa", "categoria": "FIJO"},
    {"nombre_tipo": "Seguros", "categoria": "FIJO"},
    {"nombre_tipo": "Mantenimiento de equipos", "categoria": "FIJO"},
    {"nombre_tipo": "Depreciación", "categoria": "FIJO"},
    {"nombre_tipo": "Servicios profesionales", "categoria": "FIJO"},
    {"nombre_tipo": "Gastos administrativos", "categoria": "FIJO"},
]

async def poblar_tipos_costo():
    """Pobla la tabla TipoCosto con tipos de costo básicos."""
    try:
        print("\n" + "="*70)
        print("POBLANDO TABLA: TipoCosto")
        print("="*70)
        
        await db.connect()
        print("[OK] Conectado a la base de datos")
        
        # Verificar cuántos tipos ya existen
        count_antes = await db.tipocosto.count()
        print(f"\n📊 Tipos de costo existentes antes: {count_antes}")
        
        tipos_creados = []
        tipos_existentes = []
        tipos_con_error = []
        
        print("\n" + "-"*70)
        print("INSERTANDO TIPOS DE COSTO:")
        print("-"*70)
        
        for tipo in TIPOS_COSTO:
            nombre = tipo["nombre_tipo"]
            categoria = tipo["categoria"]
            
            try:
                # Verificar si ya existe (insensible a mayúsculas/minúsculas)
                existe = await db.tipocosto.find_first(
                    where={
                        "nombre_tipo": {
                            "equals": nombre,
                            "mode": "insensitive"
                        }
                    }
                )
                
                if existe:
                    print(f"⏭️  '{nombre}' ({categoria}) - Ya existe (ID: {existe.id_tipo_costo})")
                    tipos_existentes.append(nombre)
                else:
                    # Crear nuevo tipo
                    nuevo_tipo = await db.tipocosto.create(
                        data={
                            "nombre_tipo": nombre,
                            "categoria": categoria
                        }
                    )
                    print(f"✅ '{nombre}' ({categoria}) - Creado (ID: {nuevo_tipo.id_tipo_costo})")
                    tipos_creados.append(nombre)
                    
            except Exception as e:
                print(f"❌ '{nombre}' ({categoria}) - Error: {e}")
                tipos_con_error.append({"nombre": nombre, "error": str(e)})
        
        # Resumen final
        count_despues = await db.tipocosto.count()
        
        print("\n" + "="*70)
        print("RESUMEN FINAL")
        print("="*70)
        print(f"\n📊 Tipos de costo antes: {count_antes}")
        print(f"📊 Tipos de costo después: {count_despues}")
        print(f"✅ Tipos creados: {len(tipos_creados)}")
        print(f"⏭️  Tipos que ya existían: {len(tipos_existentes)}")
        print(f"❌ Tipos con error: {len(tipos_con_error)}")
        
        if tipos_creados:
            print(f"\n✅ TIPOS CREADOS ({len(tipos_creados)}):")
            for i, nombre in enumerate(tipos_creados, 1):
                tipo_info = next(t for t in TIPOS_COSTO if t["nombre_tipo"] == nombre)
                print(f"   {i}. {nombre} ({tipo_info['categoria']})")
        
        if tipos_existentes:
            print(f"\n⏭️  TIPOS QUE YA EXISTÍAN ({len(tipos_existentes)}):")
            for i, nombre in enumerate(tipos_existentes, 1):
                print(f"   {i}. {nombre}")
        
        if tipos_con_error:
            print(f"\n❌ TIPOS CON ERROR ({len(tipos_con_error)}):")
            for i, item in enumerate(tipos_con_error, 1):
                print(f"   {i}. {item['nombre']}: {item['error']}")
        
        # Estadísticas finales
        fijos = await db.tipocosto.count(where={"categoria": "FIJO"})
        variables = await db.tipocosto.count(where={"categoria": "VARIABLE"})
        
        print(f"\n📈 ESTADÍSTICAS FINALES:")
        print(f"   Costos FIJOS: {fijos}")
        print(f"   Costos VARIABLES: {variables}")
        print(f"   Total: {count_despues}")
        
        await db.disconnect()
        print("\n[OK] Desconectado de la base de datos")
        
        if tipos_creados:
            print("\n✅ ¡Proceso completado exitosamente!")
        else:
            print("\nℹ️  No se crearon nuevos tipos (todos ya existían o hubo errores)")
        
    except Exception as e:
        print(f"\n[ERROR] Error al poblar tipos de costo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(poblar_tipos_costo())

