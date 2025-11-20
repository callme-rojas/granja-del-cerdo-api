#!/usr/bin/env python3
"""
Script para poblar la base de datos con lotes y costos asociados.
Genera escenarios variados y realistas.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random
import numpy as np

# Agregar el directorio api al path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# Cargar variables de entorno
env_path = script_dir / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"[OK] Variables de entorno cargadas desde: {env_path}")
else:
    root_env = script_dir.parent / ".env"
    if root_env.exists():
        load_dotenv(root_env)
        print(f"[OK] Variables de entorno cargadas desde: {root_env}")
    else:
        load_dotenv()
        print("[WARNING] No se encontró archivo .env, usando variables del sistema")

if not os.getenv("DATABASE_URL"):
    print("[ERROR] DATABASE_URL no encontrada en variables de entorno")
    sys.exit(1)

# Importar después de cargar variables de entorno
from db import db
from ml.data.generate_data import generar_lote
import asyncio

# Configuración
N_LOTES = 200
ID_USUARIO = 1

# Escenarios de costos por lote
ESCENARIOS_COSTOS = [
    {"nombre": "Lote básico", "probabilidad": 0.3, "min_costos": 1, "max_costos": 3},
    {"nombre": "Lote estándar", "probabilidad": 0.4, "min_costos": 3, "max_costos": 6},
    {"nombre": "Lote completo", "probabilidad": 0.2, "min_costos": 6, "max_costos": 10},
    {"nombre": "Lote premium", "probabilidad": 0.1, "min_costos": 10, "max_costos": 15},
]

async def poblar_lotes_con_costos(n_lotes: int = N_LOTES, id_usuario: int = ID_USUARIO):
    """
    Pobla la base de datos con lotes y costos asociados.
    Genera escenarios variados y realistas.
    """
    print("\n" + "="*70)
    print("POBLANDO BASE DE DATOS CON LOTES Y COSTOS")
    print("="*70)
    
    # Conectar a base de datos
    print(f"\n1. Conectando a base de datos...")
    await db.connect()
    print("[OK] Conectado a la base de datos")
    
    # Verificar usuario
    usuario = await db.usuario.find_unique(where={"id_usuario": id_usuario})
    if not usuario:
        print(f"   ⚠️  Usuario {id_usuario} no existe. Creando usuario de prueba...")
        usuario = await db.usuario.create(
            data={
                "nombre_completo": "Usuario Prueba",
                "email": f"prueba_{id_usuario}@test.com",
                "password_hash": "hash_temporal"
            }
        )
        id_usuario = usuario.id_usuario
        print(f"   ✅ Usuario creado: ID {id_usuario}")
    
    # Obtener tipos de costo disponibles
    tipos_costo = await db.tipocosto.find_many()
    if not tipos_costo:
        print("\n❌ ERROR: No hay tipos de costo en la base de datos")
        print("   Ejecuta primero: python poblar_tipos_costo.py")
        await db.disconnect()
        sys.exit(1)
    
    tipos_costo_list = [t.model_dump() if hasattr(t, 'model_dump') else t.dict() for t in tipos_costo]
    tipos_variables = [t for t in tipos_costo_list if t['categoria'] == 'VARIABLE']
    tipos_fijos = [t for t in tipos_costo_list if t['categoria'] == 'FIJO']
    
    print(f"\n2. Tipos de costo disponibles:")
    print(f"   - Variables: {len(tipos_variables)}")
    print(f"   - Fijos: {len(tipos_fijos)}")
    
    # Generar datos sintéticos
    print(f"\n3. Generando {n_lotes} lotes sintéticos...")
    df_lotes = generar_lote(n_lotes)
    
    # Preparar fechas distribuidas en 12 meses
    fecha_inicio = datetime(2024, 1, 1, 0, 0, 0)
    fechas = []
    for i in range(n_lotes):
        dias_offset = int((i / n_lotes) * 365)
        fecha = fecha_inicio + timedelta(days=dias_offset)
        fecha = fecha.replace(hour=0, minute=0, second=0, microsecond=0)
        fechas.append(fecha)
    
    df_lotes['fecha_adquisicion'] = fechas
    print(f"   ✅ {len(df_lotes)} lotes generados")
    print(f"   Rango de fechas: {min(fechas).strftime('%Y-%m-%d')} a {max(fechas).strftime('%Y-%m-%d')}")
    
    # Insertar lotes y costos
    print(f"\n4. Insertando lotes y costos en base de datos...")
    lotes_insertados = 0
    costos_insertados = 0
    
    # Estadísticas de escenarios
    escenarios_stats = {esc["nombre"]: 0 for esc in ESCENARIOS_COSTOS}
    
    for idx, row in df_lotes.iterrows():
        try:
            # Asegurar fecha válida
            fecha_adq = row.get('fecha_adquisicion')
            if fecha_adq is None or (hasattr(fecha_adq, '__iter__') and str(fecha_adq) == 'NaT'):
                dias_offset = int((idx / n_lotes) * 365)
                fecha_adq = fecha_inicio + timedelta(days=dias_offset)
            
            if isinstance(fecha_adq, str):
                try:
                    fecha_adq = datetime.strptime(fecha_adq, "%Y-%m-%d")
                except:
                    dias_offset = int((idx / n_lotes) * 365)
                    fecha_adq = fecha_inicio + timedelta(days=dias_offset)
            
            if isinstance(fecha_adq, datetime):
                fecha_adq = fecha_adq.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Crear lote
            lote = await db.lote.create(
                data={
                    "fecha_adquisicion": fecha_adq,
                    "cantidad_animales": int(row['cantidad_animales']),
                    "peso_promedio_entrada": float(row['peso_promedio_entrada']),
                    "duracion_estadia_dias": int(row['duracion_estadia_dias']),
                    "precio_compra_kg": float(row['precio_compra_kg']),
                    "id_usuario_creador": id_usuario,
                }
            )
            lotes_insertados += 1
            
            # Seleccionar escenario de costos para este lote
            rand = random.random()
            acumulado = 0
            escenario_seleccionado = None
            for esc in ESCENARIOS_COSTOS:
                acumulado += esc["probabilidad"]
                if rand <= acumulado:
                    escenario_seleccionado = esc
                    break
            
            if not escenario_seleccionado:
                escenario_seleccionado = ESCENARIOS_COSTOS[-1]
            
            escenarios_stats[escenario_seleccionado["nombre"]] += 1
            
            # Generar costos para este lote
            num_costos = random.randint(
                escenario_seleccionado["min_costos"],
                escenario_seleccionado["max_costos"]
            )
            
            # Seleccionar tipos de costo (mezclar variables y fijos)
            tipos_a_usar = []
            # 70% de probabilidad de usar costos variables
            if random.random() < 0.7 and tipos_variables:
                num_variables = min(num_costos, len(tipos_variables))
                tipos_a_usar.extend(random.sample(tipos_variables, num_variables))
            
            # 30% de probabilidad de usar costos fijos
            if random.random() < 0.3 and tipos_fijos:
                num_fijos = min(num_costos - len(tipos_a_usar), len(tipos_fijos))
                if num_fijos > 0:
                    tipos_a_usar.extend(random.sample(tipos_fijos, num_fijos))
            
            # Si no hay suficientes, completar con cualquier tipo
            while len(tipos_a_usar) < num_costos and len(tipos_a_usar) < len(tipos_costo_list):
                tipo_extra = random.choice(tipos_costo_list)
                if tipo_extra not in tipos_a_usar:
                    tipos_a_usar.append(tipo_extra)
            
            # Limitar al número de costos deseado
            tipos_a_usar = tipos_a_usar[:num_costos]
            
            # Crear costos para este lote
            for tipo_costo in tipos_a_usar:
                # Generar monto según el tipo de costo
                if tipo_costo['categoria'] == 'VARIABLE':
                    # Costos variables: dependen de cantidad de animales
                    base = random.uniform(5.0, 50.0)
                    monto = base * lote.cantidad_animales * random.uniform(0.8, 1.2)
                else:
                    # Costos fijos: montos fijos independientes de cantidad
                    monto = random.uniform(100.0, 500.0)
                
                # Redondear a 2 decimales
                monto = round(monto, 2)
                
                # Fecha del gasto: entre fecha_adquisicion y fecha_adquisicion + duracion_estadia
                dias_estadia = lote.duracion_estadia_dias or 1
                dias_offset_gasto = random.randint(0, dias_estadia)
                fecha_gasto = fecha_adq + timedelta(days=dias_offset_gasto)
                fecha_gasto = fecha_gasto.replace(hour=0, minute=0, second=0, microsecond=0)
                
                # Descripción opcional (30% de probabilidad)
                descripcion = None
                if random.random() < 0.3:
                    descripciones = [
                        f"Gasto por {tipo_costo['nombre_tipo'].lower()}",
                        f"Pago de {tipo_costo['nombre_tipo'].lower()}",
                        f"Factura de {tipo_costo['nombre_tipo'].lower()}",
                        None
                    ]
                    descripcion = random.choice(descripciones)
                
                try:
                    await db.costo.create(
                        data={
                            "id_lote": lote.id_lote,
                            "monto": monto,
                            "fecha_gasto": fecha_gasto,
                            "descripcion": descripcion,
                            "id_tipo_costo": tipo_costo['id_tipo_costo'],
                        }
                    )
                    costos_insertados += 1
                except Exception as e:
                    print(f"   ⚠️  Error creando costo para lote {lote.id_lote}: {e}")
            
            if (lotes_insertados % 50) == 0:
                print(f"   Progreso: {lotes_insertados}/{n_lotes} lotes, {costos_insertados} costos...")
                
        except Exception as e:
            print(f"   ⚠️  Error insertando lote {idx+1}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Resumen final
    print("\n" + "="*70)
    print("RESUMEN FINAL")
    print("="*70)
    print(f"\n✅ Lotes insertados: {lotes_insertados}")
    print(f"✅ Costos insertados: {costos_insertados}")
    print(f"📊 Promedio de costos por lote: {costos_insertados / lotes_insertados:.2f}" if lotes_insertados > 0 else "N/A")
    
    print(f"\n📋 Distribución de escenarios:")
    for esc_nombre, count in escenarios_stats.items():
        porcentaje = (count / lotes_insertados * 100) if lotes_insertados > 0 else 0
        print(f"   - {esc_nombre}: {count} lotes ({porcentaje:.1f}%)")
    
    # Verificar datos
    total_lotes_bd = await db.lote.count()
    total_costos_bd = await db.costo.count()
    
    print(f"\n📊 Verificación en base de datos:")
    print(f"   - Total lotes: {total_lotes_bd}")
    print(f"   - Total costos: {total_costos_bd}")
    
    await db.disconnect()
    print("\n[OK] Desconectado de la base de datos")
    print("\n✅ ¡Proceso completado exitosamente!")
    
    return lotes_insertados, costos_insertados

if __name__ == "__main__":
    # Permitir pasar el número de lotes como argumento
    n_lotes_arg = int(sys.argv[1]) if len(sys.argv) > 1 else N_LOTES
    asyncio.run(poblar_lotes_con_costos(n_lotes=n_lotes_arg))

