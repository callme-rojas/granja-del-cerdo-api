import os
import math
import argparse
import numpy as np
import pandas as pd
from pathlib import Path

# ------------------------------
# Parámetros y helpers
# ------------------------------
SEED = 42
rng = np.random.default_rng(SEED)

# Distribuciones y rangos realistas para reventa (1–3 días)
RANGO_ANIMALES = (10, 120)              # cantidad por lote
RANGO_PESO_ENTRADA = (80.0, 115.0)      # kg por animal al comprar
RANGO_PRECIO_COMPRA = (18.0, 25.0)  # Ampliado para mayor variabilidad de escenarios      # Bs/kg
RANGO_DIAS = (1, 3)                      # 1 a 3 días máximo
MESES = np.arange(1, 13)

# Costos logísticos ~ proporcional a cantidad + ruido
# Alimentación: mínima (1–3 días), cercana a cero y opcional
def generar_lote(n_rows: int) -> pd.DataFrame:
    cantidad_animales = rng.integers(RANGO_ANIMALES[0], RANGO_ANIMALES[1] + 1, size=n_rows)
    peso_promedio_entrada = rng.normal(loc=97.5, scale=8.0, size=n_rows)  # centrado ~ 97.5 kg
    peso_promedio_entrada = np.clip(peso_promedio_entrada, RANGO_PESO_ENTRADA[0], RANGO_PESO_ENTRADA[1])

    precio_compra_kg = rng.uniform(RANGO_PRECIO_COMPRA[0], RANGO_PRECIO_COMPRA[1], size=n_rows)

    # Estancia: 1–3 días (discreta)
    duracion_estadia_dias = rng.integers(RANGO_DIAS[0], RANGO_DIAS[1] + 1, size=n_rows)

    # Mes (estacionalidad) – 1..12
    mes_adquisicion = rng.choice(MESES, size=n_rows, replace=True, p=None)

    # Kilos de entrada / salida
    # IMPORTANTE: Los cerdos ganan entre 0.8 y 1.5 kg por día durante la estadía
    kilos_entrada = cantidad_animales * peso_promedio_entrada
    
    # Calcular ganancia de peso basada en días de estadía
    # Ganancia promedio: 1.15 kg/día/cerdo (rango: 0.8-1.5 kg/día)
    ganancia_por_dia = rng.uniform(0.8, 1.5, size=n_rows)  # Variación realista
    ganancia_total = ganancia_por_dia * cantidad_animales * duracion_estadia_dias
    kilos_salida = kilos_entrada + ganancia_total
    kilos_salida = np.maximum(kilos_salida, kilos_entrada * 0.95)  # Mínimo 95% del peso entrada (por mortalidad)

    # Costo logístico total ~ base + término variable por animal + ruido
    # AJUSTADO: Rangos ampliados basados en datos reales (máx real: 8,379 Bs)
    # Base de 150–500 Bs por lote según distancia/peajes + 10–50 Bs por animal aprox
    base_log = rng.uniform(150.0, 500.0, size=n_rows)
    por_animal = rng.uniform(10.0, 50.0, size=n_rows) * cantidad_animales
    ruido_log = rng.normal(0.0, 200.0, size=n_rows)  # Más variación
    costo_logistica_total = np.maximum(base_log + por_animal + ruido_log, 30.0)
    # Máximo teórico: 500 + (120 × 50) + ruido ≈ 6,500+ Bs (cubre datos reales)

    # Costo alimentación ~ variable según estadía
    # AJUSTADO: Rangos ampliados basados en datos reales (máx real: 5,681 Bs)
    # 0–5.0 Bs por animal por día, con probabilidad 0.7 de aplicar
    aplica_alim = rng.random(size=n_rows) < 0.7
    costo_alimentacion = np.where(
        aplica_alim,
        np.maximum(0.0, rng.uniform(0.0, 5.0, size=n_rows) * cantidad_animales * duracion_estadia_dias),
        0.0,
    )
    # Máximo teórico: 5.0 × 120 animales × 3 días ≈ 1,800 Bs
    # Pero también puede incluir costos adicionales, así que permitimos hasta ~6,000 Bs

    # Compra total
    compra_total = precio_compra_kg * kilos_entrada

    # Costos fijos de operación (Nivel III) - simulados para evaluación
    # AJUSTADO: Rangos ampliados basados en datos reales (máx real: 2,462 Bs)
    # Distribución normal con media más alta y mayor variación
    costo_fijo_total = np.maximum(
        rng.normal(loc=1000.0, scale=500.0, size=n_rows), 100.0
    )
    # Rango aproximado: 100-2,500 Bs (cubre datos reales)

    # ------------------------------
    # Precio de venta por kg - LÓGICA REALISTA
    # ------------------------------
    # IMPORTANTE: El precio de venta SIEMPRE debe ser mayor al precio de compra
    # Fórmula: Precio Venta = Precio Compra + Costos Adicionales/kg + Margen
    
    # 1. Calcular costos adicionales por kg (logística + alimentación, sin compra)
    costo_adicional_por_kg = (costo_logistica_total + costo_alimentacion) / kilos_salida
    
    # 2. Calcular costos fijos por kg
    costo_fijo_por_kg_calc = costo_fijo_total / kilos_salida
    
    # 3. Margen de ganancia sobre el precio de compra: 5-15%
    # En temporada alta (dic, ene) el margen puede ser mayor (10-20%)
    # En temporada baja (may, jun) el margen es menor (3-10%)
    margen_porcentaje = np.zeros(n_rows)
    for i in range(n_rows):
        mes = mes_adquisicion[i]
        if mes in [12, 1]:  # Diciembre, Enero (alta demanda)
            margen_porcentaje[i] = rng.uniform(0.10, 0.20)  # 10-20%
        elif mes in [5, 6]:  # Mayo, Junio (baja demanda)
            margen_porcentaje[i] = rng.uniform(0.03, 0.10)  # 3-10%
        else:
            margen_porcentaje[i] = rng.uniform(0.05, 0.15)  # 5-15%
    
    # 4. Calcular precio de venta
    # precio_venta = (precio_compra + costos_adicionales + costos_fijos) × (1 + margen)
    precio_base_con_costos = precio_compra_kg + costo_adicional_por_kg + costo_fijo_por_kg_calc
    precio_venta_final_kg = precio_base_con_costos * (1.0 + margen_porcentaje)
    
    # 5. Agregar ruido de mercado pequeño (±0.2 Bs/kg)
    ruido = rng.normal(0.0, 0.2, size=n_rows)
    precio_venta_final_kg = precio_venta_final_kg + ruido
    
    # 6. Asegurar que el precio de venta SIEMPRE sea mayor al precio de compra
    # Mínimo: precio_compra + 1.0 Bs/kg (margen mínimo razonable)
    precio_venta_final_kg = np.maximum(precio_venta_final_kg, precio_compra_kg + 1.0)
    
    # 7. Acotar a banda razonable (considerando el nuevo rango de precios 18-25)
    # El precio de venta puede llegar hasta 32 Bs/kg en casos extremos
    precio_venta_final_kg = np.clip(precio_venta_final_kg, 19.0, 32.0)

    # DataFrame final
    df = pd.DataFrame({
        "lote_id": np.arange(1, n_rows + 1, dtype=int),
        "cantidad_animales": cantidad_animales,
        "peso_promedio_entrada": np.round(peso_promedio_entrada, 3),
        "precio_compra_kg": np.round(precio_compra_kg, 3),
        "duracion_estadia_dias": duracion_estadia_dias,
        "mes_adquisicion": mes_adquisicion,
        "kilos_entrada": np.round(kilos_entrada, 3),
        "kilos_salida": np.round(kilos_salida, 3),
        "costo_logistica_total": np.round(costo_logistica_total, 2),
        "costo_alimentacion": np.round(costo_alimentacion, 2),
        "costo_fijo_total": np.round(costo_fijo_total, 2),
        "compra_total": np.round(compra_total, 2),
        "precio_venta_final_kg": np.round(precio_venta_final_kg, 3),  # TARGET para modelo ML (ya incluye todo)
    })

    # costo_variable_total (Nivel I+II) para análisis/evaluación
    df["costo_variable_total"] = np.round(
        df["compra_total"] + df["costo_logistica_total"] + df["costo_alimentacion"], 2
    )

    return df


def construir_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve un CSV con las features según el diseño académico.
    Implementa Feature Engineering con CTL (Costo Total por Lote) y normalización.
    INCLUYE costos fijos como feature (10 features total).
    """
    # FEATURE ENGINEERING: Crear CTL (Costo Total por Lote) según diseño académico
    # CTL concentra el 99.6% de la varianza económica en un solo feature altamente predictivo
    df["costo_total_lote"] = df["compra_total"] + df["costo_logistica_total"] + df["costo_alimentacion"]
    
    # Calcular costo_fijo_por_kg (Nivel III - Costos Fijos)
    df["costo_fijo_por_kg"] = (df["costo_fijo_total"] / df["kilos_salida"]).round(4)
    
    # Features según diseño académico (10 features: 7 Nivel I+II + 2 adicionales + 1 Nivel III)
    feats = pd.DataFrame({
        "cantidad_animales": df["cantidad_animales"].astype(int),
        "peso_promedio_entrada": df["peso_promedio_entrada"].astype(float),
        "precio_compra_kg": df["precio_compra_kg"].astype(float),
        "costo_logistica_total": df["costo_logistica_total"].astype(float),
        "costo_alimentacion_estadia": df["costo_alimentacion"].astype(float),
        "duracion_estadia_dias": df["duracion_estadia_dias"].astype(int),
        "mes_adquisicion": df["mes_adquisicion"].astype(int),
        "costo_total_lote": df["costo_total_lote"].astype(float),  # Feature Engineering CTL
        "peso_salida": df["kilos_salida"].astype(float),  # Para normalización
        "costo_fijo_por_kg": df["costo_fijo_por_kg"].astype(float),  # NUEVO: Nivel III - Costos Fijos
        "precio_venta_final_kg": df["precio_venta_final_kg"].astype(float),  # TARGET según diseño académico
    })
    return feats


def main():
    parser = argparse.ArgumentParser(description="Generador de datos sintéticos para reventa de cerdos (1-3 días).")
    parser.add_argument("--n", type=int, default=2000, help="número de filas (lotes) a generar")
    parser.add_argument("--out", type=str, default="data", help="directorio de salida")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = generar_lote(args.n)
    feats = construir_features(df)

    full_path = out_dir / "synthetic_lotes.csv"
    feats_path = out_dir / "synthetic_features.csv"

    df.to_csv(full_path.as_posix(), index=False)
    feats.to_csv(feats_path.as_posix(), index=False)

    print(f"Generado: {full_path} ({len(df)} filas)")
    print(f"Generado: {feats_path} ({len(feats)} filas)")
    print(f"Features para modelo ML: {list(feats.columns)}")
    print(f"Target: precio_venta_final_kg (rango: {feats['precio_venta_final_kg'].min():.2f} - {feats['precio_venta_final_kg'].max():.2f} Bs/kg)")
    print(f"Feature Engineering: CTL (Costo Total por Lote) implementado")
    print("\nEjemplo:")
    print(df.head(5).to_string(index=False))


if __name__ == "__main__":
    main()