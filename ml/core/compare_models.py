#!/usr/bin/env python3
"""
Script para comparar los 3 algoritmos de regresión según diseño académico:
1. Regresión Lineal Múltiple (baseline)
2. Random Forest Regressor (robusto y preciso)
3. Gradient Boosting Regressor (secuencialmente más fuerte)
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import time

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

def train_and_evaluate_model(model, model_name: str, X_train: np.ndarray, X_test: np.ndarray, 
                           y_train: np.ndarray, y_test: np.ndarray) -> dict:
    """Entrena y evalúa un modelo específico."""
    print(f"\n{'='*60}")
    print(f"ENTRENANDO: {model_name}")
    print(f"{'='*60}")
    
    # Medir tiempo de entrenamiento
    start_time = time.time()
    
    # Entrenar modelo
    model.fit(X_train, y_train)
    
    # Medir tiempo de predicción
    pred_start = time.time()
    y_pred = model.predict(X_test)
    pred_time = time.time() - pred_start
    
    train_time = time.time() - start_time
    
    # Calcular métricas
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
    
    # Análisis de errores
    errors = y_test - y_pred
    error_std = np.std(errors)
    max_error = np.max(np.abs(errors))
    
    results = {
        'model_name': model_name,
        'model': model,
        'mae': mae,
        'mse': mse,
        'rmse': rmse,
        'r2': r2,
        'mape': mape,
        'train_time': train_time,
        'pred_time': pred_time,
        'error_std': error_std,
        'max_error': max_error,
        'y_pred': y_pred
    }
    
    # Mostrar resultados
    print(f"MAE (Mean Absolute Error):     {mae:.3f} Bs/kg")
    print(f"MSE (Mean Squared Error):      {mse:.3f}")
    print(f"RMSE (Root Mean Squared Error): {rmse:.3f} Bs/kg")
    print(f"R² Score:                      {r2:.3f}")
    print(f"MAPE (Mean Absolute % Error):  {mape:.2f}%")
    print(f"Tiempo de entrenamiento:       {train_time:.2f} segundos")
    print(f"Tiempo de predicción:          {pred_time:.4f} segundos")
    print(f"Desviación estándar del error: {error_std:.3f} Bs/kg")
    print(f"Error máximo:                  {max_error:.3f} Bs/kg")
    
    return results

def compare_models():
    """Compara los 3 algoritmos según diseño académico."""
    print("COMPARACIÓN DE ALGORITMOS DE REGRESIÓN")
    print("Según diseño académico - Reventa de Cerdos")
    print("=" * 60)
    
    try:
        # Cargar datos
        df = load_data()
        
        # Preparar features y target
        X, y, feature_cols = prepare_features_target(df)
        
        # Normalización según diseño académico
        print("\nAplicando normalización (StandardScaler)...")
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # División train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        print(f"\nDivisión de datos:")
        print(f"Train samples: {len(X_train)}")
        print(f"Test samples: {len(X_test)}")
        
        # Definir los 3 algoritmos según diseño académico
        models = {
            "Regresión Lineal Múltiple": LinearRegression(),
            "Random Forest Regressor": RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ),
            "Gradient Boosting Regressor": GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
        }
        
        # Entrenar y evaluar cada modelo
        results = []
        for model_name, model in models.items():
            result = train_and_evaluate_model(
                model, model_name, X_train, X_test, y_train, y_test
            )
            results.append(result)
        
        # Comparación final
        print(f"\n{'='*80}")
        print("COMPARACIÓN FINAL DE ALGORITMOS")
        print(f"{'='*80}")
        print(f"{'Modelo':<25} {'MAE':<8} {'RMSE':<8} {'R²':<8} {'MAPE':<8} {'Tiempo':<8}")
        print("-" * 80)
        
        for result in results:
            print(f"{result['model_name']:<25} {result['mae']:<8.3f} {result['rmse']:<8.3f} "
                  f"{result['r2']:<8.3f} {result['mape']:<8.2f} {result['train_time']:<8.2f}")
        
        # Selección del mejor modelo
        best_model = min(results, key=lambda x: x['mae'])
        print(f"\nMEJOR MODELO SEGÚN MAE: {best_model['model_name']}")
        print(f"   MAE: {best_model['mae']:.3f} Bs/kg")
        print(f"   R² Score: {best_model['r2']:.3f}")
        
        # Guardar el mejor modelo
        model_data = {
            'model': best_model['model'],
            'scaler': scaler,
            'feature_cols': feature_cols,
            'target_col': 'precio_venta_final_kg',
            'model_name': best_model['model_name'],
            'metrics': {
                'mae': best_model['mae'],
                'rmse': best_model['rmse'],
                'r2': best_model['r2'],
                'mape': best_model['mape']
            }
        }
        
        # Guardar modelo
        model_path = "model_store/best_model.pkl"
        model_dir = Path(model_path).parent
        model_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(model_data, model_path)
        print(f"\nMejor modelo guardado: {model_path}")
        
        # Análisis de importancia de features (solo para modelos que lo soportan)
        print(f"\nANÁLISIS DE IMPORTANCIA DE FEATURES")
        print("=" * 50)
        
        for result in results:
            model = result['model']
            if hasattr(model, 'feature_importances_'):
                print(f"\n{result['model_name']}:")
                importances = model.feature_importances_
                feature_importance = list(zip(feature_cols, importances))
                feature_importance.sort(key=lambda x: x[1], reverse=True)
                
                for feature, importance in feature_importance:
                    print(f"  {feature:<25}: {importance:.3f}")
        
        print(f"\nComparación completada exitosamente!")
        print(f"Se evaluaron {len(models)} algoritmos según diseño académico")
        
        return results
        
    except Exception as e:
        print(f"Error durante la comparación: {e}")
        return None

if __name__ == "__main__":
    compare_models()
