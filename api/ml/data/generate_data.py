"""
Generador de datos sinteticos para modelo XGBoost con 24 features.
Simula el modelo de negocio de reventa de cerdos con estadia de 1-3 dias.

Incluye:
- Variables de adquisicion (Grupo 1)
- Logistica y transporte (Grupo 2)
- Costos fijos dinamicos con prorrateo (Grupo 3)
- Estadia, alimento y sanidad (Grupo 4)
- Variables temporales y de mercado (Grupo 5)
- Variables compuestas (Grupo 6)
"""
import os
import math
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# ------------------------------
# Parametros y helpers
# ------------------------------
SEED = 42
rng = np.random.default_rng(SEED)

# Distribuciones y rangos realistas para reventa (1-3 dias)
RANGO_ANIMALES = (10, 120)
RANGO_PESO_ENTRADA = (80.0, 115.0)
RANGO_PRECIO_COMPRA = (18.0, 25.0)
RANGO_DIAS = (1, 3)
CAPACIDAD_GRANJA = 1000  # Capacidad maxima de la granja

# Ubicaciones de origen (para calcular distancia)
UBICACIONES = ["Santa Cruz", "Beni", "Pando"]
DISTANCIAS_KM = {"Santa Cruz": 350, "Beni": 520, "Pando": 680}

# Feriados de Bolivia 2026 (para features #20 y #21)
FERIADOS_2026 = [
    datetime(2026, 1, 1),   # Año Nuevo
    datetime(2026, 1, 22),  # Dia del Estado Plurinacional
    datetime(2026, 2, 14),  # Carnaval
    datetime(2026, 2, 15),  # Carnaval
    datetime(2026, 2, 16),  # Carnaval
    datetime(2026, 4, 3),   # Viernes Santo
    datetime(2026, 5, 1),   # Dia del Trabajo
    datetime(2026, 6, 4),   # Corpus Christi
    datetime(2026, 6, 21),  # Año Nuevo Andino
    datetime(2026, 8, 6),   # Dia de la Independencia
    datetime(2026, 11, 2),  # Dia de Todos los Santos
    datetime(2026, 12, 25), # Navidad
    datetime(2026, 12, 31), # Fin de Año
]

# Costos fijos mensuales (para prorrateo)
SUELDOS_MENSUALES = 11000.0  # Bs
GASTOS_OPERATIVOS_MENSUALES = 3250.0  # Bs
SERVICIOS_BASICOS_MENSUALES = 850.0  # Bs (promedio)
MANTENIMIENTO_CAMION_MENSUAL = 3000.0  # Bs


def generar_fecha_aleatoria(year=2026):
    """Genera una fecha aleatoria en el año especificado."""
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    days_between = (end_date - start_date).days
    random_days = int(rng.integers(0, days_between + 1))
    return start_date + timedelta(days=random_days)


def calcular_feriado_proximo(fecha):
    """
    Calcula si hay un feriado en los proximos 7 dias.
    Retorna: (es_feriado_proximo, dias_para_festividad)
    """
    fecha_limite = fecha + timedelta(days=7)
    feriados_proximos = [f for f in FERIADOS_2026 if fecha <= f <= fecha_limite]
    
    if feriados_proximos:
        feriado_cercano = min(feriados_proximos)
        dias = (feriado_cercano - fecha).days
        return True, dias
    else:
        return False, 999


def generar_lote_completo(n_rows: int) -> pd.DataFrame:
    """
    Genera dataset completo con las 24 features para XGBoost.
    """
    # ========================================
    # GRUPO 1: Variables de Adquisicion
    # ========================================
    cantidad_animales = rng.integers(RANGO_ANIMALES[0], RANGO_ANIMALES[1] + 1, size=n_rows)
    peso_promedio_entrada = rng.normal(loc=97.5, scale=8.0, size=n_rows)
    peso_promedio_entrada = np.clip(peso_promedio_entrada, RANGO_PESO_ENTRADA[0], RANGO_PESO_ENTRADA[1])
    precio_compra_kg = rng.uniform(RANGO_PRECIO_COMPRA[0], RANGO_PRECIO_COMPRA[1], size=n_rows)
    
    # Feature #4: costo_adquisicion_total (calculado)
    costo_adquisicion_total = cantidad_animales * peso_promedio_entrada * precio_compra_kg
    
    # ========================================
    # GRUPO 2: Logistica y Transporte
    # ========================================
    ubicacion_origen = rng.choice(UBICACIONES, size=n_rows)
    distancia_km = np.array([DISTANCIAS_KM[loc] for loc in ubicacion_origen])
    
    # Feature #5: costo_combustible_viaje (basado en distancia)
    # Diesel: ~3.7 Bs/litro, consumo: ~25 km/litro
    litros_diesel = distancia_km / 25.0
    costo_combustible_viaje = litros_diesel * rng.uniform(3.5, 4.0, size=n_rows)
    
    # Feature #6: costo_peajes_lavado
    # Peajes: 2-4 por viaje, ~30-50 Bs cada uno + lavado 80-120 Bs
    num_peajes = rng.integers(2, 5, size=n_rows)
    costo_peajes = num_peajes * rng.uniform(30, 50, size=n_rows)
    costo_lavado = rng.uniform(80, 120, size=n_rows)
    costo_peajes_lavado = costo_peajes + costo_lavado
    
    # Feature #7: costo_flete_estimado
    # Flete: base + por km + por animal
    base_flete = rng.uniform(200, 400, size=n_rows)
    por_km = distancia_km * rng.uniform(0.5, 1.5, size=n_rows)
    por_animal = cantidad_animales * rng.uniform(5, 15, size=n_rows)
    costo_flete_estimado = base_flete + por_km + por_animal
    
    # Feature #8: mantenimiento_camion_prorrateado
    # Generar fechas para calcular viajes del mes
    fechas_adquisicion = [generar_fecha_aleatoria() for _ in range(n_rows)]
    viajes_por_mes = {}
    for fecha in fechas_adquisicion:
        mes_key = (fecha.year, fecha.month)
        viajes_por_mes[mes_key] = viajes_por_mes.get(mes_key, 0) + 1
    
    mantenimiento_camion_prorrateado = np.array([
        MANTENIMIENTO_CAMION_MENSUAL / viajes_por_mes[(fecha.year, fecha.month)]
        for fecha in fechas_adquisicion
    ])
    
    # ========================================
    # GRUPO 3: Costos Fijos Dinamicos
    # ========================================
    duracion_estadia_dias = rng.integers(RANGO_DIAS[0], RANGO_DIAS[1] + 1, size=n_rows)
    
    # Feature #9: costo_fijo_diario_lote
    costo_fijo_diario = (SUELDOS_MENSUALES + GASTOS_OPERATIVOS_MENSUALES) / 30
    costo_fijo_diario_lote = costo_fijo_diario * duracion_estadia_dias
    
    # Feature #10: factor_ocupacion_granja
    # Simular ocupacion variable (30-90% de capacidad)
    animales_en_granja = rng.integers(300, 900, size=n_rows)
    factor_ocupacion_granja = animales_en_granja / CAPACIDAD_GRANJA
    
    # Feature #11: tasa_consumo_energia_agua
    # Prorrateo de servicios basicos por animal
    animales_mes = {}
    for i, fecha in enumerate(fechas_adquisicion):
        mes_key = (fecha.year, fecha.month)
        animales_mes[mes_key] = animales_mes.get(mes_key, 0) + cantidad_animales[i]
    
    tasa_consumo_energia_agua = np.array([
        (SERVICIOS_BASICOS_MENSUALES / animales_mes[(fecha.year, fecha.month)]) * cantidad_animales[i]
        for i, fecha in enumerate(fechas_adquisicion)
    ])
    
    # Feature #12: costo_mano_obra_asignada
    costo_mano_obra_asignada = np.array([
        (SUELDOS_MENSUALES / animales_mes[(fecha.year, fecha.month)]) * cantidad_animales[i]
        for i, fecha in enumerate(fechas_adquisicion)
    ])
    
    # ========================================
    # GRUPO 4: Estadia, Alimento y Sanidad
    # ========================================
    # Feature #13: duracion_estadia_dias (ya calculado arriba)
    
    # Feature #14: costo_alimentacion_total
    # 1.5 Bs/dia/cerdo (promedio)
    costo_alimentacion_total = cantidad_animales * duracion_estadia_dias * rng.uniform(1.0, 2.0, size=n_rows)
    
    # Feature #15: costo_sanitario_total
    # Vacunas + higiene: 5-15 Bs por animal
    costo_sanitario_total = cantidad_animales * rng.uniform(5, 15, size=n_rows)
    
    # Feature #16: merma_peso_transporte
    # Perdida de 0.3-0.8 kg por cerdo durante transporte
    merma_peso_transporte = cantidad_animales * rng.uniform(0.3, 0.8, size=n_rows)
    
    # Feature #17: peso_salida_esperado
    # Ganancia de 0.8-1.5 kg/dia/cerdo
    ganancia_por_dia = rng.uniform(0.8, 1.5, size=n_rows)
    peso_ganado = ganancia_por_dia * duracion_estadia_dias
    peso_salida_promedio = peso_promedio_entrada + peso_ganado - (merma_peso_transporte / cantidad_animales)
    peso_salida_esperado = peso_salida_promedio * cantidad_animales
    
    # ========================================
    # GRUPO 5: Variables Temporales y de Mercado
    # ========================================
    # Feature #18: mes_adquisicion
    mes_adquisicion = np.array([fecha.month for fecha in fechas_adquisicion])
    
    # Feature #19: dia_semana_llegada
    dia_semana_llegada = np.array([fecha.weekday() for fecha in fechas_adquisicion])
    
    # Features #20 y #21: es_feriado_proximo, dias_para_festividad
    feriados_info = [calcular_feriado_proximo(fecha) for fecha in fechas_adquisicion]
    es_feriado_proximo = np.array([info[0] for info in feriados_info], dtype=int)
    dias_para_festividad = np.array([info[1] for info in feriados_info])
    
    # ========================================
    # GRUPO 6: Variables Compuestas
    # ========================================
    # Feature #22: costo_operativo_por_cabeza
    costo_logistica = costo_flete_estimado + costo_combustible_viaje + costo_peajes_lavado
    costo_operativo_por_cabeza = (costo_logistica + costo_fijo_diario_lote) / cantidad_animales
    
    # Feature #23: ratio_alimento_precio_compra
    ratio_alimento_precio_compra = costo_alimentacion_total / costo_adquisicion_total
    
    # Feature #24: indicador_eficiencia_estadia
    indicador_eficiencia_estadia = peso_promedio_entrada / duracion_estadia_dias
    
    # ========================================
    # TARGET: Precio de venta por kg
    # ========================================
    # Calcular precio de venta basado en costos + margen
    costo_total = (costo_adquisicion_total + costo_logistica + costo_alimentacion_total + 
                   costo_sanitario_total + costo_fijo_diario_lote)
    costo_por_kg = costo_total / peso_salida_esperado
    
    # Margen segun estacionalidad y feriados
    margen_base = np.zeros(n_rows)
    for i in range(n_rows):
        mes = mes_adquisicion[i]
        if mes in [12, 1]:  # Alta demanda
            margen_base[i] = rng.uniform(0.12, 0.22)
        elif mes in [5, 6]:  # Baja demanda
            margen_base[i] = rng.uniform(0.05, 0.12)
        else:
            margen_base[i] = rng.uniform(0.08, 0.18)
        
        # Bonus por feriado proximo
        if es_feriado_proximo[i] and dias_para_festividad[i] <= 3:
            margen_base[i] += 0.03
    
    precio_venta_kg = costo_por_kg * (1 + margen_base)
    precio_venta_kg = np.clip(precio_venta_kg, 20.0, 35.0)
    
    # ========================================
    # Crear DataFrame
    # ========================================
    df = pd.DataFrame({
        # Grupo 1: Adquisicion
        "cantidad_animales": cantidad_animales,
        "peso_promedio_entrada": np.round(peso_promedio_entrada, 2),
        "precio_compra_kg": np.round(precio_compra_kg, 2),
        "costo_adquisicion_total": np.round(costo_adquisicion_total, 2),
        
        # Grupo 2: Logistica
        "costo_combustible_viaje": np.round(costo_combustible_viaje, 2),
        "costo_peajes_lavado": np.round(costo_peajes_lavado, 2),
        "costo_flete_estimado": np.round(costo_flete_estimado, 2),
        "mantenimiento_camion_prorrateado": np.round(mantenimiento_camion_prorrateado, 2),
        
        # Grupo 3: Costos Fijos Dinamicos
        "costo_fijo_diario_lote": np.round(costo_fijo_diario_lote, 2),
        "factor_ocupacion_granja": np.round(factor_ocupacion_granja, 4),
        "tasa_consumo_energia_agua": np.round(tasa_consumo_energia_agua, 2),
        "costo_mano_obra_asignada": np.round(costo_mano_obra_asignada, 2),
        
        # Grupo 4: Estadia
        "duracion_estadia_dias": duracion_estadia_dias,
        "costo_alimentacion_total": np.round(costo_alimentacion_total, 2),
        "costo_sanitario_total": np.round(costo_sanitario_total, 2),
        "merma_peso_transporte": np.round(merma_peso_transporte, 2),
        "peso_salida_esperado": np.round(peso_salida_esperado, 2),
        
        # Grupo 5: Temporales
        "mes_adquisicion": mes_adquisicion,
        "dia_semana_llegada": dia_semana_llegada,
        "es_feriado_proximo": es_feriado_proximo,
        "dias_para_festividad": dias_para_festividad,
        
        # Grupo 6: Compuestas
        "costo_operativo_por_cabeza": np.round(costo_operativo_por_cabeza, 2),
        "ratio_alimento_precio_compra": np.round(ratio_alimento_precio_compra, 4),
        "indicador_eficiencia_estadia": np.round(indicador_eficiencia_estadia, 2),
        
        # TARGET
        "precio_venta_kg": np.round(precio_venta_kg, 2),
    })
    
    return df


def main():
    parser = argparse.ArgumentParser(description="Generador de datos sinteticos con 24 features para XGBoost.")
    parser.add_argument("--n", type=int, default=2000, help="numero de filas (lotes) a generar")
    parser.add_argument("--out", type=str, default="../../../data", help="directorio de salida")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generando {args.n} lotes con 24 features...")
    df = generar_lote_completo(args.n)

    output_path = out_dir / "dataset_xgboost_24_features.csv"
    df.to_csv(output_path.as_posix(), index=False)

    print(f"\n✅ Generado: {output_path} ({len(df)} filas)")
    print(f"\n📊 Features generadas: {len(df.columns) - 1} features + 1 target")
    print(f"   Target: precio_venta_kg (rango: {df['precio_venta_kg'].min():.2f} - {df['precio_venta_kg'].max():.2f} Bs/kg)")
    
    print(f"\n📋 Grupos de features:")
    print(f"   Grupo 1 (Adquisicion): 4 features")
    print(f"   Grupo 2 (Logistica): 4 features")
    print(f"   Grupo 3 (Costos Fijos): 4 features")
    print(f"   Grupo 4 (Estadia): 5 features")
    print(f"   Grupo 5 (Temporales): 4 features")
    print(f"   Grupo 6 (Compuestas): 3 features")
    print(f"   TOTAL: 24 features")
    
    print(f"\n🔍 Ejemplo de datos:")
    print(df.head(3).to_string(index=False))
    
    print(f"\n📈 Estadisticas:")
    print(f"   Lotes con feriado proximo: {df['es_feriado_proximo'].sum()} ({df['es_feriado_proximo'].sum()/len(df)*100:.1f}%)")
    print(f"   Ocupacion granja promedio: {df['factor_ocupacion_granja'].mean():.2%}")
    print(f"   Duracion estadia promedio: {df['duracion_estadia_dias'].mean():.1f} dias")


if __name__ == "__main__":
    main()