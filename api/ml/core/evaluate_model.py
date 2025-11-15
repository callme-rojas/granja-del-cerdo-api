#!/usr/bin/env python3
"""
Script para evaluar el modelo ML entrenado.
Calcula métricas de rendimiento y genera reportes.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from pathlib import Path

def load_model(model_path: str = "models/12_months_model.pkl"):
    """Carga el modelo entrenado y el scaler según diseño académico."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Modelo no encontrado: {model_path}")
    
    model_data = joblib.load(model_path)
    print(f"Modelo cargado: {model_path}")
    print(f"Features: {model_data['feature_names']}")
    print(f"Target: {model_data['target_name']}")
    return model_data

def load_test_data(data_path: str = "docs/dataset_12_meses.csv"):
    """Carga datos de prueba."""
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset no encontrado: {data_path}")
    
    df = pd.read_csv(data_path)
    print(f"Dataset de prueba: {len(df)} filas")
    return df

def evaluate_model(model_data: dict, df: pd.DataFrame):
    """Evalúa el modelo con métricas completas según diseño académico."""
    model = model_data['model']
    scaler = model_data['scaler']
    feature_cols = model_data['feature_names']
    target_col = model_data['target_name']
    
    # Preparar datos
    X = df[feature_cols].values
    y_true = df[target_col].values
    
    # Aplicar normalización
    X_scaled = scaler.transform(X)
    
    # Predicciones
    y_pred = model.predict(X_scaled)
    
    # Métricas
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)
    
    # Métricas adicionales
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    max_error = np.max(np.abs(y_true - y_pred))
    
    print("\nMÉTRICAS DE EVALUACIÓN")
    print("=" * 40)
    print(f"MAE (Mean Absolute Error):     {mae:.3f} Bs/kg")
    print(f"MSE (Mean Squared Error):      {mse:.3f}")
    print(f"RMSE (Root Mean Squared Error): {rmse:.3f} Bs/kg")
    print(f"R² Score:                      {r2:.3f}")
    print(f"MAPE (Mean Absolute % Error):  {mape:.2f}%")
    print(f"Max Error:                     {max_error:.3f} Bs/kg")
    
    # Análisis de errores
    errors = y_true - y_pred
    print(f"\nANÁLISIS DE ERRORES")
    print("=" * 40)
    print(f"Error promedio:                {np.mean(errors):.3f} Bs/kg")
    print(f"Desviación estándar:           {np.std(errors):.3f} Bs/kg")
    print(f"Error mínimo:                  {np.min(errors):.3f} Bs/kg")
    print(f"Error máximo:                  {np.max(errors):.3f} Bs/kg")
    
    # Percentiles de error
    percentiles = [25, 50, 75, 90, 95, 99]
    print(f"\nPERCENTILES DE ERROR ABSOLUTO")
    print("=" * 40)
    abs_errors = np.abs(errors)
    for p in percentiles:
        val = np.percentile(abs_errors, p)
        print(f"P{p}: {val:.3f} Bs/kg")
    
    return {
        "mae": mae,
        "mse": mse,
        "rmse": rmse,
        "r2": r2,
        "mape": mape,
        "max_error": max_error,
        "mean_error": np.mean(errors),
        "std_error": np.std(errors)
    }

def analyze_feature_importance(model, feature_cols):
    """Analiza la importancia de las features."""
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        
        print(f"\nIMPORTANCIA DE FEATURES")
        print("=" * 40)
        
        # Crear DataFrame con importancias
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        for _, row in feature_importance.iterrows():
            print(f"{row['feature']:<25}: {row['importance']:.3f}")
        
        return feature_importance
    else:
        print("El modelo no soporta análisis de importancia de features")
        return None

def generate_sample_predictions(model_data: dict, df: pd.DataFrame, n_samples: int = 5):
    """Genera predicciones de ejemplo según diseño académico."""
    model = model_data['model']
    scaler = model_data['scaler']
    feature_cols = model_data['feature_names']
    target_col = model_data['target_name']
    
    # Tomar muestras aleatorias
    sample_df = df.sample(n=n_samples, random_state=42)
    X_sample = sample_df[feature_cols].values
    y_true_sample = sample_df[target_col].values
    
    # Aplicar normalización
    X_sample_scaled = scaler.transform(X_sample)
    y_pred_sample = model.predict(X_sample_scaled)
    
    print(f"\nPREDICCIONES DE EJEMPLO")
    print("=" * 60)
    print(f"{'Feature':<20} {'Real':<8} {'Pred':<8} {'Error':<8}")
    print("-" * 60)
    
    for i in range(n_samples):
        error = y_true_sample[i] - y_pred_sample[i]
        print(f"Lote {i+1:<15} {y_true_sample[i]:<8.2f} {y_pred_sample[i]:<8.2f} {error:<8.2f}")

def main():
    """Función principal."""
    print("Evaluación de modelo ML para reventa de cerdos")
    print("=" * 50)
    
    try:
        # Cargar modelo y datos
        model_data = load_model()
        df = load_test_data()
        
        # Evaluar modelo
        metrics = evaluate_model(model_data, df)
        
        # Analizar importancia de features
        feature_cols = model_data['feature_cols']
        feature_importance = analyze_feature_importance(model_data['model'], feature_cols)
        
        # Generar predicciones de ejemplo
        generate_sample_predictions(model_data, df)
        
        print(f"\nEvaluación completada")
        print(f"El modelo tiene un MAE de {metrics['mae']:.3f} Bs/kg")
        print(f"R² Score de {metrics['r2']:.3f}")
        
        if metrics['mae'] < 0.5:
            print("Excelente rendimiento del modelo!")
        elif metrics['mae'] < 1.0:
            print("Buen rendimiento del modelo")
        else:
            print("El modelo podría necesitar mejoras")
        
    except Exception as e:
        print(f"Error durante la evaluación: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
