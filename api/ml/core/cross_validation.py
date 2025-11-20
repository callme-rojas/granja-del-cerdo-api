#!/usr/bin/env python3
"""
Módulo de Validación Cruzada para evaluación robusta del modelo.
Implementa K-Fold Cross-Validation con métricas MAE y RMSE según objetivo específico 1.1.1.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, cross_validate
from sklearn.metrics import mean_absolute_error, mean_squared_error, make_scorer
from typing import Dict, List, Tuple, Any
import time


def calculate_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calcula el Mean Absolute Error (MAE)."""
    return mean_absolute_error(y_true, y_pred)


def calculate_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calcula el Root Mean Squared Error (RMSE)."""
    mse = mean_squared_error(y_true, y_pred)
    return np.sqrt(mse)


def cross_validation_evaluation(
    model: Any,
    X: np.ndarray,
    y: np.ndarray,
    cv_folds: int = 5,
    random_state: int = 42,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Realiza validación cruzada K-Fold completa con métricas MAE y RMSE.
    
    Esta función implementa el método de validación cruzada descrito en el objetivo
    específico 1.1.1, dividiendo el conjunto de datos en varios subconjuntos y evaluando
    el modelo en diferentes combinaciones para obtener una medida más fiable de precisión.
    
    Args:
        model: Modelo de sklearn a evaluar
        X: Features (array numpy)
        y: Target (array numpy)
        cv_folds: Número de folds para validación cruzada (default: 5)
        random_state: Semilla para reproducibilidad
        verbose: Si True, imprime resultados detallados
    
    Returns:
        Diccionario con métricas de validación cruzada incluyendo:
        - test_mae: Estadísticas de MAE en conjunto de prueba
        - test_rmse: Estadísticas de RMSE en conjunto de prueba
        - train_mae: Estadísticas de MAE en conjunto de entrenamiento
        - train_rmse: Estadísticas de RMSE en conjunto de entrenamiento
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"VALIDACIÓN CRUZADA K-FOLD (K={cv_folds})")
        print(f"{'='*70}")
        print(f"Total de muestras: {len(X):,}")
        print(f"Features: {X.shape[1]}")
        print(f"Target range: {y.min():.2f} - {y.max():.2f} Bs/kg")
    
    # Crear K-Fold splitter
    kfold = KFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
    
    # Definir métricas personalizadas
    scoring = {
        'mae': make_scorer(mean_absolute_error),
        'mse': make_scorer(mean_squared_error),
        'neg_mae': 'neg_mean_absolute_error',
        'neg_mse': 'neg_mean_squared_error'
    }
    
    # Realizar validación cruzada
    start_time = time.time()
    cv_results = cross_validate(
        model, X, y,
        cv=kfold,
        scoring=scoring,
        return_train_score=True,
        return_estimator=False,
        n_jobs=-1
    )
    cv_time = time.time() - start_time
    
    # Calcular RMSE a partir de MSE
    cv_results['test_rmse'] = np.sqrt(cv_results['test_mse'])
    cv_results['train_rmse'] = np.sqrt(cv_results['train_mse'])
    
    # Calcular estadísticas agregadas
    metrics_summary = {
        'cv_folds': cv_folds,
        'cv_time': cv_time,
        'test_mae': {
            'mean': cv_results['test_mae'].mean(),
            'std': cv_results['test_mae'].std(),
            'min': cv_results['test_mae'].min(),
            'max': cv_results['test_mae'].max(),
            'scores': cv_results['test_mae'].tolist()
        },
        'test_rmse': {
            'mean': cv_results['test_rmse'].mean(),
            'std': cv_results['test_rmse'].std(),
            'min': cv_results['test_rmse'].min(),
            'max': cv_results['test_rmse'].max(),
            'scores': cv_results['test_rmse'].tolist()
        },
        'train_mae': {
            'mean': cv_results['train_mae'].mean(),
            'std': cv_results['train_mae'].std()
        },
        'train_rmse': {
            'mean': cv_results['train_rmse'].mean(),
            'std': cv_results['train_rmse'].std()
        },
        'raw_results': cv_results
    }
    
    if verbose:
        print(f"\nRESULTADOS DE VALIDACIÓN CRUZADA")
        print(f"{'='*70}")
        print(f"\n📊 MÉTRICAS EN CONJUNTO DE PRUEBA (TEST):")
        print(f"   MAE:  {metrics_summary['test_mae']['mean']:.4f} ± {metrics_summary['test_mae']['std']:.4f} Bs/kg")
        print(f"   RMSE: {metrics_summary['test_rmse']['mean']:.4f} ± {metrics_summary['test_rmse']['std']:.4f} Bs/kg")
        print(f"   Rango MAE:  [{metrics_summary['test_mae']['min']:.4f}, {metrics_summary['test_mae']['max']:.4f}] Bs/kg")
        print(f"   Rango RMSE: [{metrics_summary['test_rmse']['min']:.4f}, {metrics_summary['test_rmse']['max']:.4f}] Bs/kg")
        
        print(f"\n📈 MÉTRICAS EN CONJUNTO DE ENTRENAMIENTO (TRAIN):")
        print(f"   MAE:  {metrics_summary['train_mae']['mean']:.4f} ± {metrics_summary['train_mae']['std']:.4f} Bs/kg")
        print(f"   RMSE: {metrics_summary['train_rmse']['mean']:.4f} ± {metrics_summary['train_rmse']['std']:.4f} Bs/kg")
        
        print(f"\n📋 RESULTADOS POR FOLD:")
        print(f"   {'Fold':<8} {'MAE (Test)':<15} {'RMSE (Test)':<15} {'MAE (Train)':<15} {'RMSE (Train)':<15}")
        print(f"   {'-'*70}")
        for i in range(cv_folds):
            print(f"   {i+1:<8} "
                  f"{cv_results['test_mae'][i]:<15.4f} "
                  f"{cv_results['test_rmse'][i]:<15.4f} "
                  f"{cv_results['train_mae'][i]:<15.4f} "
                  f"{cv_results['train_rmse'][i]:<15.4f}")
        
        print(f"\n⏱️  Tiempo total de validación cruzada: {cv_time:.2f} segundos")
        
        # Análisis de sobreajuste
        overfitting_mae = metrics_summary['train_mae']['mean'] - metrics_summary['test_mae']['mean']
        overfitting_rmse = metrics_summary['train_rmse']['mean'] - metrics_summary['test_rmse']['mean']
        
        print(f"\n🔍 ANÁLISIS DE SOBREAJUSTE:")
        print(f"   Diferencia MAE (Train-Test):  {overfitting_mae:.4f} Bs/kg")
        print(f"   Diferencia RMSE (Train-Test): {overfitting_rmse:.4f} Bs/kg")
        
        if abs(overfitting_mae) < 0.1:
            print(f"   ✅ El modelo muestra buen equilibrio (sin sobreajuste significativo)")
        elif overfitting_mae > 0.2:
            print(f"   ⚠️  Posible sobreajuste detectado (train mucho mejor que test)")
        else:
            print(f"   ℹ️  El modelo generaliza bien")
    
    return metrics_summary


def compare_models_cross_validation(
    models: Dict[str, Any],
    X: np.ndarray,
    y: np.ndarray,
    cv_folds: int = 5,
    random_state: int = 42
) -> pd.DataFrame:
    """
    Compara múltiples modelos usando validación cruzada.
    
    Args:
        models: Diccionario con nombre_modelo: modelo
        X: Features
        y: Target
        cv_folds: Número de folds
        random_state: Semilla
    
    Returns:
        DataFrame con resultados comparativos ordenados por MAE
    """
    print(f"\n{'='*70}")
    print(f"COMPARACIÓN DE MODELOS CON VALIDACIÓN CRUZADA")
    print(f"{'='*70}")
    
    all_results = []
    
    for model_name, model in models.items():
        print(f"\nEvaluando: {model_name}")
        print("-" * 70)
        
        cv_metrics = cross_validation_evaluation(
            model, X, y, cv_folds=cv_folds, 
            random_state=random_state, verbose=False
        )
        
        all_results.append({
            'Modelo': model_name,
            'MAE_Media': cv_metrics['test_mae']['mean'],
            'MAE_Std': cv_metrics['test_mae']['std'],
            'RMSE_Media': cv_metrics['test_rmse']['mean'],
            'RMSE_Std': cv_metrics['test_rmse']['std'],
            'MAE_Min': cv_metrics['test_mae']['min'],
            'MAE_Max': cv_metrics['test_mae']['max'],
            'RMSE_Min': cv_metrics['test_rmse']['min'],
            'RMSE_Max': cv_metrics['test_rmse']['max'],
            'Tiempo_CV': cv_metrics['cv_time']
        })
    
    # Crear DataFrame comparativo
    df_comparison = pd.DataFrame(all_results)
    df_comparison = df_comparison.sort_values('MAE_Media')
    
    print(f"\n{'='*70}")
    print(f"TABLA COMPARATIVA DE MODELOS")
    print(f"{'='*70}")
    print(df_comparison.to_string(index=False))
    
    # Mejor modelo
    best_model = df_comparison.iloc[0]
    print(f"\n🏆 MEJOR MODELO (según MAE): {best_model['Modelo']}")
    print(f"   MAE:  {best_model['MAE_Media']:.4f} ± {best_model['MAE_Std']:.4f} Bs/kg")
    print(f"   RMSE: {best_model['RMSE_Media']:.4f} ± {best_model['RMSE_Std']:.4f} Bs/kg")
    
    return df_comparison


def generate_cross_validation_report(
    model: Any,
    model_name: str,
    X: np.ndarray,
    y: np.ndarray,
    cv_folds: int = 5,
    output_path: str = None
) -> Dict[str, Any]:
    """
    Genera un reporte completo de validación cruzada.
    
    Args:
        model: Modelo a evaluar
        model_name: Nombre del modelo
        X: Features
        y: Target
        cv_folds: Número de folds
        output_path: Ruta para guardar reporte (opcional)
    
    Returns:
        Diccionario con reporte completo estructurado
    """
    print(f"\n{'='*70}")
    print(f"GENERANDO REPORTE DE VALIDACIÓN CRUZADA")
    print(f"Modelo: {model_name}")
    print(f"{'='*70}")
    
    # Realizar validación cruzada
    cv_metrics = cross_validation_evaluation(
        model, X, y, cv_folds=cv_folds, verbose=True
    )
    
    # Crear reporte estructurado
    report = {
        'model_name': model_name,
        'validation_method': 'K-Fold Cross-Validation',
        'cv_folds': cv_folds,
        'total_samples': len(X),
        'metrics': {
            'mae': {
                'mean': cv_metrics['test_mae']['mean'],
                'std': cv_metrics['test_mae']['std'],
                'interpretation': interpret_mae(cv_metrics['test_mae']['mean'])
            },
            'rmse': {
                'mean': cv_metrics['test_rmse']['mean'],
                'std': cv_metrics['test_rmse']['std'],
                'interpretation': interpret_rmse(cv_metrics['test_rmse']['mean'])
            }
        },
        'fold_results': [
            {
                'fold': i+1,
                'mae': cv_metrics['test_mae']['scores'][i],
                'rmse': cv_metrics['test_rmse']['scores'][i]
            }
            for i in range(cv_folds)
        ],
        'overfitting_analysis': {
            'mae_difference': cv_metrics['train_mae']['mean'] - cv_metrics['test_mae']['mean'],
            'rmse_difference': cv_metrics['train_rmse']['mean'] - cv_metrics['test_rmse']['mean'],
            'status': 'good' if abs(cv_metrics['train_mae']['mean'] - cv_metrics['test_mae']['mean']) < 0.1 else 'potential_overfitting'
        },
        'recommendation': generate_recommendation(cv_metrics)
    }
    
    # Guardar reporte si se especifica ruta
    if output_path:
        import json
        from pathlib import Path
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Reporte guardado en: {output_path}")
    
    return report


def interpret_mae(mae_value: float) -> str:
    """Interpreta el valor de MAE para decisiones estratégicas."""
    if mae_value < 0.5:
        return "Excelente precisión. El modelo es muy confiable para fijación de precios estratégicos."
    elif mae_value < 1.0:
        return "Buena precisión. El modelo es confiable para decisiones de precios."
    elif mae_value < 2.0:
        return "Precisión aceptable. Útil para estimaciones generales, pero considerar márgenes de seguridad."
    else:
        return "Precisión limitada. Se recomienda mejorar el modelo antes de usarlo para decisiones críticas."


def interpret_rmse(rmse_value: float) -> str:
    """Interpreta el valor de RMSE para decisiones estratégicas."""
    if rmse_value < 0.7:
        return "Excelente precisión. Errores grandes son poco frecuentes."
    elif rmse_value < 1.5:
        return "Buena precisión. Errores grandes son moderados."
    elif rmse_value < 3.0:
        return "Precisión aceptable. Puede haber errores grandes ocasionalmente."
    else:
        return "Precisión limitada. Errores grandes pueden ser frecuentes."


def generate_recommendation(cv_metrics: Dict[str, Any]) -> str:
    """Genera recomendación basada en los resultados de validación cruzada."""
    mae_mean = cv_metrics['test_mae']['mean']
    mae_std = cv_metrics['test_mae']['std']
    overfitting = abs(cv_metrics['train_mae']['mean'] - cv_metrics['test_mae']['mean'])
    
    recommendations = []
    
    if mae_mean < 0.5:
        recommendations.append("✅ El modelo tiene excelente precisión y es altamente recomendable para uso en producción.")
    elif mae_mean < 1.0:
        recommendations.append("✅ El modelo tiene buena precisión y es adecuado para uso en producción.")
    else:
        recommendations.append("⚠️ Se recomienda mejorar el modelo antes de usarlo en producción.")
    
    if mae_std > mae_mean * 0.3:
        recommendations.append("⚠️ Alta variabilidad entre folds. Considerar más datos o ajustar hiperparámetros.")
    
    if overfitting > 0.2:
        recommendations.append("⚠️ Posible sobreajuste detectado. Considerar regularización o simplificar el modelo.")
    
    return " ".join(recommendations)

