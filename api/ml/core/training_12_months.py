#!/usr/bin/env python3

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import (
    train_test_split, cross_val_score, KFold,
    GridSearchCV, RandomizedSearchCV
)
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    make_scorer, explained_variance_score
)
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.feature_selection import SelectKBest, f_regression, RFE
from sklearn.pipeline import Pipeline
from pathlib import Path
import time
import warnings
warnings.filterwarnings('ignore')

# Importar módulo de validación cruzada
from ml.core.cross_validation import cross_validation_evaluation

def generate_12_months_dataset() -> pd.DataFrame:
    """Genera dataset realista para 12 meses de operación."""
    print("Generando dataset de 12 meses de operación...")
    print("Estrategia: 1 semana por mes = 12 semanas totales")
    
    np.random.seed(42)
    
    # Calcular número de lotes para 12 meses
    # 1 semana por mes × 12 meses × 2-3 lotes por semana = ~24-36 lotes por mes
    # Total: 12 meses × 30 lotes/mes = 360 lotes
    n_lotes = 360  # Más realista para 12 meses
    
    print(f"Generando {n_lotes} lotes para 12 meses de operación...")
    
    # Generar datos realistas para reventa (1-3 días)
    cantidad_animales = np.random.choice(
        [15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100], 
        size=n_lotes
    )
    
    peso_promedio_entrada = np.random.normal(100, 12, n_lotes)
    peso_promedio_entrada = np.clip(peso_promedio_entrada, 75, 125)
    
    precio_compra_kg = np.random.normal(18.5, 2.0, n_lotes)
    precio_compra_kg = np.clip(precio_compra_kg, 15, 22)
    
    duracion_estadia_dias = np.random.choice([1, 2, 3], size=n_lotes, p=[0.5, 0.3, 0.2])
    
    # Meses con estacionalidad realista
    mes_adquisicion = np.random.choice(range(1, 13), size=n_lotes)
    
    # Cálculos realistas
    kilos_entrada = cantidad_animales * peso_promedio_entrada
    
    # Variación mínima de peso (reventa corta)
    variacion_peso = np.random.normal(0, 0.01, n_lotes)  # ±1% variación
    kilos_salida = kilos_entrada * (1 + variacion_peso)
    
    # Costos logísticos realistas - AJUSTADO con rangos más amplios
    costo_logistica_base = np.random.normal(600, 200, n_lotes)
    costo_logistica_variable = cantidad_animales * np.random.normal(20, 10, n_lotes)
    costo_logistica_total = np.maximum(costo_logistica_base + costo_logistica_variable, 100.0)
    
    # Alimentación mínima (1-3 días)
    costo_alimentacion = np.zeros(n_lotes)
    for i in range(n_lotes):
        if duracion_estadia_dias[i] > 1:
            if np.random.random() > 0.4:  # 60% probabilidad de alimentación
                costo_alimentacion[i] = cantidad_animales[i] * duracion_estadia_dias[i] * np.random.normal(1.0, 0.2)
    
    # Costos fijos realistas - AJUSTADO con rangos más amplios
    costo_fijo_total = np.random.normal(1000, 500, n_lotes)
    costo_fijo_total = np.clip(costo_fijo_total, 100, 2500)
    
    compra_total = kilos_entrada * precio_compra_kg
    
    # Precio base con estacionalidad realista
    margen_base = np.random.normal(2.0, 0.5, n_lotes)
    
    # Estacionalidad más pronunciada para 12 meses
    estacionalidad = np.zeros(n_lotes)
    for i in range(n_lotes):
        mes = mes_adquisicion[i]
        if mes in [12, 1]:  # Diciembre, Enero (alta demanda)
            estacionalidad[i] = np.random.uniform(0.3, 1.0)
        elif mes in [4, 5]:  # Abril, Mayo (baja demanda)
            estacionalidad[i] = np.random.uniform(-0.6, -0.1)
        elif mes in [6, 7, 8]:  # Verano (demanda media)
            estacionalidad[i] = np.random.uniform(-0.2, 0.2)
        else:  # Resto del año
            estacionalidad[i] = np.random.uniform(-0.3, 0.3)
    
    precio_base_kg = precio_compra_kg + margen_base + estacionalidad
    precio_base_kg = np.clip(precio_base_kg, 16, 25)
    
    # Crear DataFrame
    df = pd.DataFrame({
        "lote_id": range(1, n_lotes + 1),
        "cantidad_animales": cantidad_animales,
        "peso_promedio_entrada": peso_promedio_entrada,
        "precio_compra_kg": precio_compra_kg,
        "duracion_estadia_dias": duracion_estadia_dias,
        "mes_adquisicion": mes_adquisicion,
        "kilos_entrada": kilos_entrada,
        "kilos_salida": kilos_salida,
        "costo_logistica_total": costo_logistica_total,
        "costo_alimentacion": costo_alimentacion,
        "costo_fijo_total": costo_fijo_total,
        "compra_total": compra_total,
        "precio_base_kg": precio_base_kg,
    })
    
    # Feature Engineering CTL
    df["costo_total_lote"] = df["compra_total"] + df["costo_logistica_total"] + df["costo_alimentacion"]
    
    # Precio final con margen
    margen_backend = 0.10
    df["precio_venta_final_kg"] = (
        (df["precio_base_kg"] + df["costo_fijo_total"] / df["kilos_salida"]) * (1 + margen_backend)
    ).round(3)
    
    # Features para modelo - INCLUYENDO COSTOS FIJOS
    # IMPORTANTE: El modelo debe recibir costos fijos para predecir correctamente el precio
    df["costo_fijo_por_kg"] = (df["costo_fijo_total"] / df["kilos_salida"]).round(4)
    
    features_df = pd.DataFrame({
        "cantidad_animales": df["cantidad_animales"].astype(int),
        "peso_promedio_entrada": df["peso_promedio_entrada"].astype(float),
        "precio_compra_kg": df["precio_compra_kg"].astype(float),
        "costo_logistica_total": df["costo_logistica_total"].astype(float),
        "costo_alimentacion_estadia": df["costo_alimentacion"].astype(float),
        "duracion_estadia_dias": df["duracion_estadia_dias"].astype(int),
        "mes_adquisicion": df["mes_adquisicion"].astype(int),
        "costo_total_lote": df["costo_total_lote"].astype(float),
        "peso_salida": df["kilos_salida"].astype(float),
        "costo_fijo_por_kg": df["costo_fijo_por_kg"].astype(float),  # NUEVO: Costos Fijos como feature
        "precio_venta_final_kg": df["precio_venta_final_kg"].astype(float),
    })
    
    print(f"Dataset de 12 meses generado:")
    print(f"- Total lotes: {len(features_df):,}")
    print(f"- Features: {len(features_df.columns)-1}")
    print(f"- Target range: {features_df['precio_venta_final_kg'].min():.2f} - {features_df['precio_venta_final_kg'].max():.2f} Bs/kg")
    
    # Análisis por mes
    print(f"\nDistribución por mes:")
    for mes in range(1, 13):
        count = len(features_df[features_df['mes_adquisicion'] == mes])
        print(f"- Mes {mes:2d}: {count:3d} lotes")
    
    return features_df

def comprehensive_model_comparison(X: np.ndarray, y: np.ndarray, feature_names: list) -> dict:
    """Comparación exhaustiva de modelos con dataset de 12 meses."""
    print(f"\nComparación Exhaustiva de Modelos")
    print(f"Dataset: {len(X):,} muestras, {len(feature_names)} features")
    
    # División de datos
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Normalización
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Definir modelos según diseño académico (solo 3 algoritmos)
    models = {
        'LinearRegression': LinearRegression(),
        'RandomForest': RandomForestRegressor(
            n_estimators=100, max_depth=10, min_samples_split=5, 
            min_samples_leaf=2, random_state=42
        ),
        'GradientBoosting': GradientBoostingRegressor(
            n_estimators=100, learning_rate=0.1, max_depth=6,
            min_samples_split=5, random_state=42
        )
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"\n{'='*70}")
        print(f"EVALUANDO: {name}")
        print(f"{'='*70}")
        
        # ========== VALIDACIÓN CRUZADA ==========
        print(f"\n1. VALIDACIÓN CRUZADA (K-Fold)")
        cv_metrics = cross_validation_evaluation(
            model, X_train_scaled, y_train, 
            cv_folds=5, random_state=42, verbose=True
        )
        
        # ========== EVALUACIÓN EN TEST SET ==========
        print(f"\n2. EVALUACIÓN EN CONJUNTO DE PRUEBA")
        # Entrenar modelo con todos los datos de entrenamiento
        start_time = time.time()
        model.fit(X_train_scaled, y_train)
        train_time = time.time() - start_time
        
        # Predicciones en test
        start_time = time.time()
        y_pred = model.predict(X_test_scaled)
        pred_time = time.time() - start_time
        
        # Métricas en test set
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        evs = explained_variance_score(y_test, y_pred)
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
        
        # Análisis de errores
        errors = y_test - y_pred
        error_std = np.std(errors)
        max_error = np.max(np.abs(errors))
        
        results[name] = {
            'model': model,
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'r2': r2,
            'evs': evs,
            'mape': mape,
            'train_time': train_time,
            'pred_time': pred_time,
            'error_std': error_std,
            'max_error': max_error,
            'y_pred': y_pred,
            # Métricas de validación cruzada
            'cv_mae_mean': cv_metrics['test_mae']['mean'],
            'cv_mae_std': cv_metrics['test_mae']['std'],
            'cv_rmse_mean': cv_metrics['test_rmse']['mean'],
            'cv_rmse_std': cv_metrics['test_rmse']['std'],
            'cv_metrics': cv_metrics
        }
        
        print(f"\n📊 RESUMEN DE MÉTRICAS:")
        print(f"   Test Set - MAE:  {mae:.3f} Bs/kg")
        print(f"   Test Set - RMSE: {rmse:.3f} Bs/kg")
        print(f"   CV - MAE:  {cv_metrics['test_mae']['mean']:.3f} ± {cv_metrics['test_mae']['std']:.3f} Bs/kg")
        print(f"   CV - RMSE: {cv_metrics['test_rmse']['mean']:.3f} ± {cv_metrics['test_rmse']['std']:.3f} Bs/kg")
        print(f"   R²: {r2:.3f}")
    
    # IMPORTANTE: Verificar que el scaler esté fitted
    if not hasattr(scaler, 'n_features_in_'):
        print("\n⚠️ WARNING: El scaler no está fitted. Re-fitting con todo el dataset...")
        scaler.fit(X)
        print(f"✅ Scaler fitted con {scaler.n_features_in_} features")
    
    return results, scaler, feature_names

# Función ensemble_analysis eliminada - NO está en el diseño académico

def feature_importance_analysis(results: dict, feature_names: list) -> None:
    """Análisis de importancia de features."""
    print(f"\nAnálisis de Importancia de Features...")
    print("=" * 60)
    
    for name, result in results.items():
        model = result['model']
        if hasattr(model, 'feature_importances_'):
            print(f"\n{name}:")
            importances = model.feature_importances_
            feature_importance = list(zip(feature_names, importances))
            feature_importance.sort(key=lambda x: x[1], reverse=True)
            
            for feature, importance in feature_importance:
                print(f"  {feature:<25}: {importance:.3f}")

def save_final_model(results: dict, scaler: StandardScaler, feature_names: list) -> str:
    """Guarda el mejor modelo encontrado."""
    # Seleccionar el mejor modelo por MAE
    best_name = min(results.keys(), key=lambda x: results[x]['mae'])
    best_result = results[best_name]
    
    print(f"\nMEJOR MODELO: {best_name}")
    print(f"MAE: {best_result['mae']:.3f} Bs/kg")
    print(f"R²: {best_result['r2']:.3f}")
    print(f"CV MAE: {best_result['cv_mae_mean']:.3f} (+/- {best_result['cv_mae_std']:.3f})")
    
    # Preparar datos para guardar
    model_data = {
        'model': best_result['model'],
        'scaler': scaler,
        'feature_names': feature_names,
        'target_name': 'precio_venta_final_kg',
        'model_name': best_name,
        'metrics': {
            'mae': best_result['mae'],
            'rmse': best_result['rmse'],
            'r2': best_result['r2'],
            'mape': best_result['mape'],
            'cv_mae_mean': best_result['cv_mae_mean'],
            'cv_mae_std': best_result['cv_mae_std'],
            'cv_rmse_mean': best_result['cv_rmse_mean'],
            'cv_rmse_std': best_result['cv_rmse_std']
        },
        'all_results': results,
        'dataset_info': {
            'total_samples': len(feature_names),
            'months_covered': 12,
            'strategy': '1 semana por mes'
        }
    }
    
    # Guardar modelo en la ubicación correcta (ml/models/)
    # Calcular path absoluto desde la raíz del proyecto (api/)
    try:
        # Intentar usar __file__ si está disponible
        script_dir = Path(__file__).parent.parent.parent  # api/
    except NameError:
        # Si __file__ no está disponible, usar el directorio actual y subir 2 niveles
        script_dir = Path.cwd()
        # Si estamos en api/ml/core, subir 2 niveles
        if script_dir.name == "core" and script_dir.parent.name == "ml":
            script_dir = script_dir.parent.parent  # api/
        elif script_dir.name == "api":
            pass  # Ya estamos en api/
        else:
            # Buscar api/ en el path
            for parent in script_dir.parents:
                if parent.name == "api":
                    script_dir = parent
                    break
    
    model_path = script_dir / "ml" / "models" / "12_months_model.pkl"
    model_dir = model_path.parent
    model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_data, str(model_path))
    
    print(f"Modelo de 12 meses guardado: {model_path}")
    return str(model_path)

def main():
    """Función principal del entrenamiento de 12 meses."""
    print("ENTRENAMIENTO PROFESIONAL - 12 MESES DE DATOS")
    print("=" * 50)
    print("Estrategia: 1 semana por mes = 12 semanas totales")
    print("=" * 50)
    
    try:
        # 1. Generar dataset de 12 meses
        df = generate_12_months_dataset()
        
        # 2. Preparar features y target - INCLUYENDO COSTOS FIJOS
        feature_cols = [
            "cantidad_animales", "peso_promedio_entrada", "precio_compra_kg",
            "costo_logistica_total", "costo_alimentacion_estadia", "duracion_estadia_dias",
            "mes_adquisicion", "costo_total_lote", "peso_salida",
            "costo_fijo_por_kg"  # NUEVO: Costos Fijos como feature
        ]
        
        X = df[feature_cols].values
        y = df["precio_venta_final_kg"].values
        
        print(f"\nDataset preparado:")
        print(f"Features: {len(feature_cols)}")
        print(f"Muestras: {len(X):,}")
        print(f"Target range: {y.min():.2f} - {y.max():.2f} Bs/kg")
        
        # 3. Comparación exhaustiva de modelos
        results, scaler, feature_names = comprehensive_model_comparison(X, y, feature_cols)
        
        # 4. Análisis de ensemble (NO incluido en diseño académico)
        # results = ensemble_analysis(results, X, y)
        
        # 5. Análisis de importancia de features
        feature_importance_analysis(results, feature_cols)
        
        # 6. Guardar mejor modelo
        model_path = save_final_model(results, scaler, feature_cols)
        
        # 7. Resumen final
        print(f"\n" + "="*60)
        print("RESUMEN FINAL - ENTRENAMIENTO DE 12 MESES")
        print("="*60)
        
        # Mostrar ranking de modelos
        sorted_results = sorted(results.items(), key=lambda x: x[1]['mae'])
        print(f"\nRANKING DE MODELOS:")
        for i, (name, result) in enumerate(sorted_results, 1):
            print(f"{i}. {name:<20}: MAE = {result['mae']:.3f} Bs/kg, R² = {result['r2']:.3f}")
        
        print(f"\nEntrenamiento de 12 meses completado exitosamente!")
        print(f"Se evaluaron {len(results)} modelos diferentes")
        print(f"Mejor modelo: {min(results.keys(), key=lambda x: results[x]['mae'])}")
        print(f"Modelo guardado en: {model_path}")
        
        return results
        
    except Exception as e:
        print(f"Error durante el entrenamiento: {e}")
        return None

if __name__ == "__main__":
    main()
