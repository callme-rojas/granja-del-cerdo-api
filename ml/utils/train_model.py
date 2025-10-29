#!/usr/bin/env python3
"""
Script para entrenar modelo de ML para predicción de precios en reventa de cerdos.
Usa RandomForestRegressor con las 7 features del backend.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
from pathlib import Path

def load_data(data_path: str = "data/synthetic_features.csv") -> pd.DataFrame:
    """Carga el dataset de features generado."""
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset no encontrado: {data_path}")
    
    df = pd.read_csv(data_path)
    print(f"Dataset cargado: {len(df)} filas, {len(df.columns)} columnas")
    return df

def prepare_features_target(df: pd.DataFrame) -> tuple:
    """Prepara features X y target y para el modelo según diseño académico."""
    # Features según diseño académico (7 features + CTL + peso_salida para normalización)
    feature_cols = [
        "cantidad_animales",
        "peso_promedio_entrada", 
        "precio_compra_kg",
        "costo_logistica_total",
        "costo_alimentacion_estadia",
        "duracion_estadia_dias",
        "mes_adquisicion",
        "costo_total_lote",  # Feature Engineering CTL
        "peso_salida"  # Para normalización
    ]
    
    # Verificar que todas las features existen
    missing_cols = [col for col in feature_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Features faltantes: {missing_cols}")
    
    X = df[feature_cols].values
    y = df["precio_venta_final_kg"].values  # Target según diseño académico
    
    print(f"Features: {feature_cols}")
    print(f"Target: precio_venta_final_kg (rango: {y.min():.2f} - {y.max():.2f} Bs/kg)")
    
    return X, y, feature_cols

def train_model(X: np.ndarray, y: np.ndarray) -> tuple:
    """Entrena el modelo RandomForestRegressor con normalización según diseño académico."""
    print("\nAplicando normalización (StandardScaler)...")
    
    # Normalización según diseño académico
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Dividir datos
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    
    # Configurar modelo
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    # Entrenar
    model.fit(X_train, y_train)
    
    # Evaluar
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Modelo entrenado exitosamente")
    print(f"MAE: {mae:.3f} Bs/kg")
    print(f"R² Score: {r2:.3f}")
    print(f"Train samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    
    return model, scaler

def save_model(model_data: dict, model_path: str = "model_store/latest.pkl"):
    """Guarda el modelo entrenado y el scaler según diseño académico."""
    model_dir = Path(model_path).parent
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Guardar modelo, scaler y metadata
    joblib.dump(model_data, model_path)
    print(f"Modelo guardado: {model_path}")

def main():
    """Función principal."""
    print("Entrenamiento de modelo ML para reventa de cerdos")
    print("=" * 50)
    
    try:
        # Cargar datos
        df = load_data()
        
        # Preparar features y target
        X, y, feature_cols = prepare_features_target(df)
        
        # Entrenar modelo
        model, scaler = train_model(X, y)
        
        # Preparar datos para guardar
        model_data = {
            'model': model,
            'scaler': scaler,
            'feature_cols': feature_cols,
            'target_col': 'precio_venta_final_kg'
        }
        
        # Guardar modelo
        save_model(model_data)
        
        print("\nEntrenamiento completado exitosamente!")
        print("El modelo está listo para usar en el backend")
        
    except Exception as e:
        print(f"Error durante el entrenamiento: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
