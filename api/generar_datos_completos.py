"""
Script Único para Poblar Base de Datos
Genera 100 lotes con todas las relaciones correctas
Ejecutar desde: cd api && python generar_datos_completos.py
"""
import asyncio
from db import db
from datetime import datetime, timedelta
import random

# ==================== CONFIGURACIÓN ====================
NUM_LOTES = 100
MESES_HISTORICOS = 6

# ==================== DATOS BASE ====================

TIPOS_COSTO_DATA = [
    {"nombre_tipo": "Alimentación", "categoria": "VARIABLE"},
    {"nombre_tipo": "Transporte", "categoria": "VARIABLE"},
    {"nombre_tipo": "Sanitario", "categoria": "VARIABLE"},
    {"nombre_tipo": "Mano de Obra", "categoria": "FIJO"},
    {"nombre_tipo": "Servicios Básicos", "categoria": "FIJO"},
    {"nombre_tipo": "Mantenimiento", "categoria": "FIJO"},
]

FERIADOS_DATA = [
    # 2024
    {"nombre_feriado": "Año Nuevo", "fecha": "2024-01-01"},
    {"nombre_feriado": "Carnaval", "fecha": "2024-02-12"},
    {"nombre_feriado": "Carnaval", "fecha": "2024-02-13"},
    {"nombre_feriado": "Viernes Santo", "fecha": "2024-03-29"},
    {"nombre_feriado": "Día del Trabajo", "fecha": "2024-05-01"},
    {"nombre_feriado": "Corpus Christi", "fecha": "2024-05-30"},
    {"nombre_feriado": "Año Nuevo Andino", "fecha": "2024-06-21"},
    {"nombre_feriado": "Día de la Independencia", "fecha": "2024-08-06"},
    {"nombre_feriado": "Todos Santos", "fecha": "2024-11-02"},
    {"nombre_feriado": "Navidad", "fecha": "2024-12-25"},
    # 2025
    {"nombre_feriado": "Año Nuevo", "fecha": "2025-01-01"},
    {"nombre_feriado": "Carnaval", "fecha": "2025-03-03"},
    {"nombre_feriado": "Carnaval", "fecha": "2025-03-04"},
    {"nombre_feriado": "Viernes Santo", "fecha": "2025-04-18"},
    {"nombre_feriado": "Día del Trabajo", "fecha": "2025-05-01"},
    {"nombre_feriado": "Corpus Christi", "fecha": "2025-06-19"},
    {"nombre_feriado": "Año Nuevo Andino", "fecha": "2025-06-21"},
    {"nombre_feriado": "Día de la Independencia", "fecha": "2025-08-06"},
    {"nombre_feriado": "Todos Santos", "fecha": "2025-11-02"},
    {"nombre_feriado": "Navidad", "fecha": "2025-12-25"},
    # 2026
    {"nombre_feriado": "Año Nuevo", "fecha": "2026-01-01"},
    {"nombre_feriado": "Carnaval", "fecha": "2026-02-16"},
    {"nombre_feriado": "Carnaval", "fecha": "2026-02-17"},
    {"nombre_feriado": "Viernes Santo", "fecha": "2026-04-03"},
    {"nombre_feriado": "Día del Trabajo", "fecha": "2026-05-01"},
    {"nombre_feriado": "Día de la Independencia", "fecha": "2026-08-06"},
    {"nombre_feriado": "Navidad", "fecha": "2026-12-25"},
]

UBICACIONES = ["Santa Cruz", "Cochabamba", "La Paz", "Tarija", "Beni", "Pando"]

# ==================== FUNCIONES AUXILIARES ====================

def generar_fecha_aleatoria(meses_atras=6):
    """Genera una fecha aleatoria en los últimos N meses"""
    dias_atras = random.randint(0, meses_atras * 30)
    return datetime.now() - timedelta(days=dias_atras)

def generar_lote_realista():
    """Genera datos realistas para un lote"""
    # Distribución: 40% pequeño, 40% mediano, 20% grande
    rand = random.random()
    if rand < 0.4:
        cantidad = random.randint(8, 12)
    elif rand < 0.8:
        cantidad = random.randint(13, 16)
    else:
        cantidad = random.randint(17, 20)
    
    return {
        "cantidad_animales": cantidad,
        "peso_promedio_entrada": round(random.uniform(65, 90), 2),
        "precio_compra_kg": round(random.uniform(18, 24), 2),
        "duracion_estadia_dias": random.randint(15, 35),
        "fecha_adquisicion": generar_fecha_aleatoria(MESES_HISTORICOS),
        "ubicacion_origen": random.choice(UBICACIONES),
        # Costos logísticos opcionales
        "costo_flete": round(random.uniform(300, 600), 2) if random.random() > 0.2 else None,
        "costo_combustible": round(random.uniform(150, 300), 2) if random.random() > 0.3 else None,
        "costo_peajes_lavado": round(random.uniform(50, 150), 2) if random.random() > 0.4 else None,
        "merma_peso_transporte": round(random.uniform(0.5, 3.0), 2) if random.random() > 0.5 else None,
    }

# ==================== FUNCIONES DE POBLACIÓN ====================

async def poblar_tipos_costo():
    """Poblar tipos de costo"""
    print("1️⃣ Poblando Tipos de Costo...")
    count = 0
    for tipo in TIPOS_COSTO_DATA:
        existing = await db.tipocosto.find_first(where={"nombre_tipo": tipo["nombre_tipo"]})
        if not existing:
            await db.tipocosto.create(data=tipo)
            count += 1
    print(f"   ✅ {count} tipos de costo creados")
    return await db.tipocosto.find_many()

async def poblar_feriados():
    """Poblar feriados"""
    print("2️⃣ Poblando Feriados...")
    count = 0
    for feriado in FERIADOS_DATA:
        fecha = datetime.strptime(feriado["fecha"], "%Y-%m-%d")
        existing = await db.feriado.find_first(where={"fecha": fecha})
        if not existing:
            await db.feriado.create(data={
                "nombre_feriado": feriado["nombre_feriado"],
                "fecha": fecha
            })
            count += 1
    print(f"   ✅ {count} feriados creados")

async def poblar_gastos_mensuales(tipos_costo):
    """Poblar gastos mensuales para los últimos meses"""
    print("3️⃣ Poblando Gastos Mensuales...")
    
    tipo_servicios = next((t for t in tipos_costo if "Servicios" in t.nombre_tipo), None)
    tipo_mano_obra = next((t for t in tipos_costo if "Mano" in t.nombre_tipo), None)
    tipo_mantenimiento = next((t for t in tipos_costo if "Mantenimiento" in t.nombre_tipo), None)
    
    if not tipo_servicios or not tipo_mano_obra:
        print("   ⚠️ Tipos de costo no encontrados")
        return
    
    count = 0
    fecha_actual = datetime.now()
    
    for i in range(MESES_HISTORICOS):
        mes_fecha = fecha_actual - timedelta(days=30 * i)
        mes = mes_fecha.month
        anio = mes_fecha.year
        
        gastos = [
            {"id_tipo_costo": tipo_servicios.id_tipo_costo, "descripcion": "Electricidad", 
             "monto": round(1200 + random.uniform(-200, 200), 2)},
            {"id_tipo_costo": tipo_servicios.id_tipo_costo, "descripcion": "Agua", 
             "monto": round(800 + random.uniform(-150, 150), 2)},
            {"id_tipo_costo": tipo_mano_obra.id_tipo_costo, "descripcion": "Salarios", 
             "monto": 8000},
        ]
        
        if tipo_mantenimiento:
            gastos.append({
                "id_tipo_costo": tipo_mantenimiento.id_tipo_costo, 
                "descripcion": "Mantenimiento General",
                "monto": round(1500 + random.uniform(-300, 300), 2)
            })
        
        for gasto in gastos:
            try:
                existing = await db.gastomensual.find_first(where={
                    "mes": mes,
                    "anio": anio,
                    "id_tipo_costo": gasto["id_tipo_costo"],
                    "descripcion": gasto["descripcion"]
                })
                
                if not existing:
                    await db.gastomensual.create(data={
                        **gasto,
                        "mes": mes,
                        "anio": anio,
                        "fecha_registro": mes_fecha.replace(day=1)
                    })
                    count += 1
            except:
                pass  # Ignorar duplicados por restricción única
    
    print(f"   ✅ {count} gastos mensuales creados")

async def poblar_lotes(tipos_costo):
    """Poblar 100 lotes con costos y producción"""
    print(f"4️⃣ Poblando {NUM_LOTES} Lotes...")
    
    tipo_alimentacion = next((t for t in tipos_costo if t.nombre_tipo == "Alimentación"), None)
    tipo_sanitario = next((t for t in tipos_costo if t.nombre_tipo == "Sanitario"), None)
    tipo_transporte = next((t for t in tipos_costo if t.nombre_tipo == "Transporte"), None)
    
    lotes_creados = 0
    costos_creados = 0
    producciones_creadas = 0
    
    for i in range(NUM_LOTES):
        try:
            # Generar datos del lote
            lote_data = generar_lote_realista()
            
            # Crear lote
            lote = await db.lote.create(data=lote_data)
            lotes_creados += 1
            
            # Crear costos para el lote
            cantidad = lote.cantidad_animales
            duracion = lote.duracion_estadia_dias or 20
            fecha_adq = lote.fecha_adquisicion
            
            # Costo de Alimentación (siempre)
            if tipo_alimentacion:
                await db.costo.create(data={
                    "id_lote": lote.id_lote,
                    "id_tipo_costo": tipo_alimentacion.id_tipo_costo,
                    "monto": round(cantidad * duracion * random.uniform(8, 12), 2),
                    "fecha_gasto": fecha_adq + timedelta(days=duracion // 2),
                    "descripcion": "Alimento balanceado"
                })
                costos_creados += 1
            
            # Costo Sanitario (siempre)
            if tipo_sanitario:
                await db.costo.create(data={
                    "id_lote": lote.id_lote,
                    "id_tipo_costo": tipo_sanitario.id_tipo_costo,
                    "monto": round(cantidad * random.uniform(15, 25), 2),
                    "fecha_gasto": fecha_adq + timedelta(days=random.randint(1, 7)),
                    "descripcion": "Vacunas y desparasitación"
                })
                costos_creados += 1
            
            # Costo de Transporte (80% de lotes)
            if tipo_transporte and random.random() > 0.2:
                await db.costo.create(data={
                    "id_lote": lote.id_lote,
                    "id_tipo_costo": tipo_transporte.id_tipo_costo,
                    "monto": round(random.uniform(300, 600), 2),
                    "fecha_gasto": fecha_adq,
                    "descripcion": "Flete y combustible"
                })
                costos_creados += 1
            
            # Crear Producción (70% de lotes)
            if random.random() > 0.3:
                peso_entrada_total = lote.peso_promedio_entrada * cantidad
                # Ganancia de peso: 15-25 kg por animal
                ganancia_peso = random.uniform(15, 25) * cantidad
                merma = lote.merma_peso_transporte or 0
                peso_salida = peso_entrada_total + ganancia_peso - merma
                
                await db.produccion.create(data={
                    "id_lote": lote.id_lote,
                    "peso_salida_total": round(peso_salida, 2),
                    "mortalidad_unidades": random.randint(0, 2) if random.random() > 0.8 else 0
                })
                producciones_creadas += 1
            
            # Progreso cada 10 lotes
            if (i + 1) % 10 == 0:
                print(f"   📊 Progreso: {i + 1}/{NUM_LOTES} lotes")
        
        except Exception as e:
            print(f"   ⚠️ Error en lote {i + 1}: {e}")
    
    print(f"   ✅ {lotes_creados} lotes creados")
    print(f"   ✅ {costos_creados} costos creados")
    print(f"   ✅ {producciones_creadas} producciones creadas")

# ==================== FUNCIÓN PRINCIPAL ====================

async def main():
    """Función principal de población"""
    print("=" * 60)
    print("🚀 GENERACIÓN DE DATOS COMPLETOS")
    print("=" * 60)
    print(f"📊 Configuración:")
    print(f"   - Lotes a crear: {NUM_LOTES}")
    print(f"   - Meses históricos: {MESES_HISTORICOS}")
    print(f"   - Tipos de costo: {len(TIPOS_COSTO_DATA)}")
    print(f"   - Feriados: {len(FERIADOS_DATA)}")
    print("=" * 60)
    print()
    
    try:
        await db.connect()
        
        # 1. Tipos de Costo
        tipos_costo = await poblar_tipos_costo()
        
        # 2. Feriados
        await poblar_feriados()
        
        # 3. Gastos Mensuales
        await poblar_gastos_mensuales(tipos_costo)
        
        # 4. Lotes (con costos y producción)
        await poblar_lotes(tipos_costo)
        
        # Resumen final
        print()
        print("=" * 60)
        print("✅ POBLACIÓN COMPLETADA")
        print("=" * 60)
        
        total_tipos = await db.tipocosto.count()
        total_feriados = await db.feriado.count()
        total_gastos = await db.gastomensual.count()
        total_lotes = await db.lote.count()
        total_costos = await db.costo.count()
        total_produccion = await db.produccion.count()
        
        print(f"📊 Resumen de Base de Datos:")
        print(f"   - Tipos de Costo: {total_tipos}")
        print(f"   - Feriados: {total_feriados}")
        print(f"   - Gastos Mensuales: {total_gastos}")
        print(f"   - Lotes: {total_lotes}")
        print(f"   - Costos: {total_costos}")
        print(f"   - Producciones: {total_produccion}")
        print()
        print("🎉 ¡Sistema listo para usar!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
