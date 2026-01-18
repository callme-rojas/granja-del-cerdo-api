#!/usr/bin/env python3
"""
Script para inicializar la base de datos con datos esenciales.
Ejecutar después de crear la base de datos en Render.

Uso:
    python scripts/init_database.py
"""
import sys
import asyncio
from pathlib import Path

# Agregar api al path
api_dir = Path(__file__).parent.parent / "api"
sys.path.insert(0, str(api_dir))

from db import db
from passlib.hash import bcrypt

async def init_database():
    """Inicializa la base de datos con datos esenciales."""
    print("\n" + "="*70)
    print("INICIALIZANDO BASE DE DATOS")
    print("="*70)
    
    await db.connect()
    
    try:
        # 1. Crear rol por defecto
        print("\n1. Creando rol 'admin'...")
        rol = await db.rol.upsert(
            where={"nombre_rol": "admin"},
            data={
                "create": {"nombre_rol": "admin"},
                "update": {}
            }
        )
        print(f"   ✅ Rol 'admin' creado/verificado (ID: {rol.id_rol})")
        
        # 2. Crear usuario por defecto
        print("\n2. Creando usuario por defecto...")
        password_hash = bcrypt.hash("granjacerdo")
        usuario = await db.usuario.upsert(
            where={"email": "dayanadelgadillo@granja.com"},
            data={
                "create": {
                    "nombre_completo": "Dayana Delgadillo",
                    "email": "dayanadelgadillo@granja.com",
                    "password_hash": password_hash,
                    "id_rol": rol.id_rol
                },
                "update": {}
            }
        )
        print(f"   ✅ Usuario creado/verificado (ID: {usuario.id_usuario})")
        print(f"   📧 Email: dayanadelgadillo@granja.com")
        print(f"   🔑 Password: granjacerdo")
        
        # 3. Crear tipos de costo básicos
        print("\n3. Creando tipos de costo básicos...")
        tipos_costo = [
            {"nombre_tipo": "Alimentación", "categoria": "VARIABLE"},
            {"nombre_tipo": "Logística", "categoria": "VARIABLE"},
            {"nombre_tipo": "Transporte", "categoria": "VARIABLE"},
            {"nombre_tipo": "Veterinario", "categoria": "VARIABLE"},
            {"nombre_tipo": "Medicamentos", "categoria": "VARIABLE"},
            {"nombre_tipo": "Mantenimiento de Instalaciones", "categoria": "FIJO"},
            {"nombre_tipo": "Servicios Básicos", "categoria": "FIJO"},
            {"nombre_tipo": "Alquiler de Instalaciones", "categoria": "FIJO"},
            {"nombre_tipo": "Mano de Obra Administrativa", "categoria": "FIJO"},
        ]
        
        for tipo in tipos_costo:
            await db.tipocosto.upsert(
                where={"nombre_tipo": tipo["nombre_tipo"]},
                data={
                    "create": tipo,
                    "update": {}
                }
            )
            print(f"   ✅ Tipo de costo '{tipo['nombre_tipo']}' ({tipo['categoria']})")
        
        # 4. Verificar totales
        print("\n4. Verificando datos...")
        total_roles = await db.rol.count()
        total_usuarios = await db.usuario.count()
        total_tipos = await db.tipocosto.count()
        
        print(f"   📊 Total roles: {total_roles}")
        print(f"   📊 Total usuarios: {total_usuarios}")
        print(f"   📊 Total tipos de costo: {total_tipos}")
        
        print("\n" + "="*70)
        print("✅ BASE DE DATOS INICIALIZADA CORRECTAMENTE")
        print("="*70)
        print("\n💡 Puedes iniciar sesión con:")
        print("   Email: dayanadelgadillo@granja.com")
        print("   Password: granjacerdo")
        print()
        
    except Exception as e:
        print(f"\n❌ Error al inicializar base de datos: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(init_database())
