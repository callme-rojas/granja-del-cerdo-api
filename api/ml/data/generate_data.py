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
RANGO_PRECIO_COMPRA = (16.0, 20.0)      # Bs/kg
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

    # Kilos de entrada / salida (apequeña merma o leve ganancia por hidratación)
    # Para reventa tan corta, la variación es mínima: [-0.5%, +0.5%]
    factor_variacion = rng.normal(loc=0.0, scale=0.003, size=n_rows)  # ~0.3% std
    kilos_entrada = cantidad_animales * peso_promedio_entrada
    kilos_salida = kilos_entrada * (1.0 + factor_variacion)
    kilos_salida = np.maximum(kilos_salida, 1.0)

    # Costo logístico total ~ base + término variable por animal + ruido
    # Base de 150–350 Bs por lote según distancia/peajes + 10–25 Bs por animal aprox
    base_log = rng.uniform(150.0, 350.0, size=n_rows)
    por_animal = rng.uniform(10.0, 25.0, size=n_rows) * cantidad_animales
    ruido_log = rng.normal(0.0, 60.0, size=n_rows)
    costo_logistica_total = np.maximum(base_log + por_animal + ruido_log, 30.0)

    # Costo alimentación ~ casi cero (si días > 1, agrega un pequeño costo)
    # 0–1.2 Bs por animal por día, con probabilidad 0.6 de aplicar
    aplica_alim = rng.random(size=n_rows) < 0.6
    costo_alimentacion = np.where(
        aplica_alim,
        np.maximum(0.0, rng.uniform(0.0, 1.2, size=n_rows) * cantidad_animales * np.maximum(0, duracion_estadia_dias - 1)),
        0.0,
    )

    # Compra total
    compra_total = precio_compra_kg * kilos_entrada

    # Costos fijos de operación (Nivel III) - simulados para evaluación,
    # el modelo NO los usa; el backend los suma en /predict.
    costo_fijo_total = np.maximum(
        rng.normal(loc=500.0, scale=200.0, size=n_rows), 120.0
    )

    # ------------------------------
    # Precio base por kg (target para el modelo ML)
    # ------------------------------
    # El modelo predice precio_base_kg, el backend añade costos fijos + margen

    # Construimos un "precio base" a partir de precio_compra_kg + márgenes + efectos:
    # - Margen bruto base: 1.2–2.8 Bs/kg (sin costos fijos)
    # - Estacionalidad por mes: +[0..1.0] Bs/kg en meses altos, -[0..0.6] en meses bajos
    # - Penalización leve por logística/kg si es muy alta
    # - Ruido de mercado

    margen_bruto = rng.uniform(1.2, 2.8, size=n_rows)  # Reducido (sin costos fijos)

    # Estacionalidad por mes (ejemplo simple):
    # Meses altos: dic(12), ene(1) → +[0.3..1.0]
    # Meses bajos: abr(4), may(5)   → -[0.2..0.6]
    estacionalidad = np.zeros(n_rows)
    altos = (mes_adquisicion == 12) | (mes_adquisicion == 1)
    bajos = (mes_adquisicion == 4) | (mes_adquisicion == 5)
    estacionalidad = np.where(altos, rng.uniform(0.3, 1.0, size=n_rows), estacionalidad)
    estacionalidad = np.where(bajos, -rng.uniform(0.2, 0.6, size=n_rows), estacionalidad)

    # Penalización por logística por kg (si logística es muy alta para el lote)
    logistica_por_kg = costo_logistica_total / kilos_salida
    penal_logistica = np.clip(logistica_por_kg - 0.25, 0.0, 1.0) * rng.uniform(0.15, 0.4, size=n_rows)

    ruido = rng.normal(0.0, 0.25, size=n_rows)  # ruido de mercado reducido

    precio_base_kg = precio_compra_kg + margen_bruto + estacionalidad - penal_logistica + ruido

    # Acotar a banda razonable 17–22 (precio base, sin costos fijos)
    precio_base_kg = np.clip(precio_base_kg, 17.0, 22.0)

    # Ligeros outliers (1%) para robustez
    mask_out = rng.random(size=n_rows) < 0.01
    precio_base_kg[mask_out] += rng.uniform(-0.6, 0.8, size=mask_out.sum())
    precio_base_kg = np.clip(precio_base_kg, 16.5, 22.5)

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
        "costo_fijo_total": np.round(costo_fijo_total, 2),  # Nivel III (backend)
        "compra_total": np.round(compra_total, 2),
        "precio_base_kg": np.round(precio_base_kg, 3),    # TARGET para modelo ML
    })

    # costo_variable_total (Nivel I+II) para análisis/evaluación
    df["costo_variable_total"] = np.round(
        df["compra_total"] + df["costo_logistica_total"] + df["costo_alimentacion"], 2
    )

    # precio_venta_final_kg (para validación manual - precio_base + costos fijos + margen)
    margen_backend = 0.10  # 10% margen del backend
    df["precio_venta_final_kg"] = np.round(
        (df["precio_base_kg"] + df["costo_fijo_total"] / df["kilos_salida"]) * (1 + margen_backend), 3
    )

    return df


def construir_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve un CSV con las features según el diseño académico.
    Implementa Feature Engineering con CTL (Costo Total por Lote) y normalización.
    """
    # FEATURE ENGINEERING: Crear CTL (Costo Total por Lote) según diseño académico
    # CTL concentra el 99.6% de la varianza económica en un solo feature altamente predictivo
    df["costo_total_lote"] = df["compra_total"] + df["costo_logistica_total"] + df["costo_alimentacion"]
    
    # Features según diseño académico (7 features + CTL)
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