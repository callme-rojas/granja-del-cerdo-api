"""
Script de entrenamiento del modelo XGBoost con 24 features.
Incluye K-Fold Cross-Validation, Feature Importance y metricas de evaluacion.
"""
import pandas as pd
import numpy as np
import pickle
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb

# Configuracion
SEED = 42
K_FOLDS = 5
DATA_PATH = Path("../../data/dataset_xgboost_24_features.csv")
MODEL_OUTPUT_PATH = Path("ml/models/xgboost_24_features.pkl")
FEATURE_IMPORTANCE_PATH = Path("ml/models/feature_importance.png")

# Crear directorios si no existen
MODEL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def cargar_datos():
    """Carga el dataset y separa features del target."""
    print("📂 Cargando dataset...")
    df = pd.read_csv(DATA_PATH)
    
    # Separar features y target
    target_col = "precio_venta_kg"
    feature_cols = [col for col in df.columns if col != target_col]
    
    X = df[feature_cols]
    y = df[target_col]
    
    print(f"✅ Dataset cargado: {len(df)} filas, {len(feature_cols)} features")
    print(f"   Target: {target_col} (rango: {y.min():.2f} - {y.max():.2f} Bs/kg)")
    
    return X, y, feature_cols


def entrenar_modelo(X, y):
    """Entrena el modelo XGBoost con los mejores hiperparametros."""
    print("\n🤖 Entrenando modelo XGBoost...")
    
    # Hiperparametros optimizados para regresion
    params = {
        'objective': 'reg:squarederror',
        'max_depth': 6,
        'learning_rate': 0.1,
        'n_estimators': 200,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'min_child_weight': 3,
        'gamma': 0.1,
        'reg_alpha': 0.1,
        'reg_lambda': 1.0,
        'random_state': SEED,
        'n_jobs': -1
    }
    
    modelo = xgb.XGBRegressor(**params)
    modelo.fit(X, y)
    
    print("✅ Modelo entrenado")
    return modelo


def validacion_cruzada(modelo, X, y):
    """Realiza K-Fold Cross-Validation y calcula metricas."""
    print(f"\n📊 Validacion cruzada (K={K_FOLDS})...")
    
    kfold = KFold(n_splits=K_FOLDS, shuffle=True, random_state=SEED)
    
    # Calcular MAE con cross-validation
    mae_scores = -cross_val_score(
        modelo, X, y, 
        cv=kfold, 
        scoring='neg_mean_absolute_error',
        n_jobs=-1
    )
    
    # Calcular RMSE con cross-validation
    mse_scores = -cross_val_score(
        modelo, X, y, 
        cv=kfold, 
        scoring='neg_mean_squared_error',
        n_jobs=-1
    )
    rmse_scores = np.sqrt(mse_scores)
    
    # Calcular R² con cross-validation
    r2_scores = cross_val_score(
        modelo, X, y, 
        cv=kfold, 
        scoring='r2',
        n_jobs=-1
    )
    
    print(f"\n📈 Resultados de Validacion Cruzada:")
    print(f"   MAE:  {mae_scores.mean():.4f} ± {mae_scores.std():.4f} Bs/kg")
    print(f"   RMSE: {rmse_scores.mean():.4f} ± {rmse_scores.std():.4f} Bs/kg")
    print(f"   R²:   {r2_scores.mean():.4f} ± {r2_scores.std():.4f}")
    
    return {
        'mae_mean': mae_scores.mean(),
        'mae_std': mae_scores.std(),
        'rmse_mean': rmse_scores.mean(),
        'rmse_std': rmse_scores.std(),
        'r2_mean': r2_scores.mean(),
        'r2_std': r2_scores.std()
    }


def evaluar_modelo_completo(modelo, X, y):
    """Evalua el modelo en el dataset completo."""
    print("\n🎯 Evaluacion en dataset completo...")
    
    y_pred = modelo.predict(X)
    
    mae = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    r2 = r2_score(y, y_pred)
    
    print(f"   MAE:  {mae:.4f} Bs/kg")
    print(f"   RMSE: {rmse:.4f} Bs/kg")
    print(f"   R²:   {r2:.4f}")
    
    return {'mae': mae, 'rmse': rmse, 'r2': r2}


def graficar_feature_importance(modelo, feature_cols):
    """Genera grafica de Feature Importance."""
    print("\n📊 Generando grafica de Feature Importance...")
    
    # Obtener importancias
    importances = modelo.feature_importances_
    feature_importance_df = pd.DataFrame({
        'feature': feature_cols,
        'importance': importances
    }).sort_values('importance', ascending=False)
    
    # Crear grafica
    plt.figure(figsize=(12, 8))
    sns.barplot(
        data=feature_importance_df.head(15),
        x='importance',
        y='feature',
        palette='viridis'
    )
    plt.title('Top 15 Features - Importancia en Modelo XGBoost', fontsize=16, fontweight='bold')
    plt.xlabel('Importancia', fontsize=12)
    plt.ylabel('Feature', fontsize=12)
    plt.tight_layout()
    
    # Guardar
    plt.savefig(FEATURE_IMPORTANCE_PATH, dpi=300, bbox_inches='tight')
    print(f"✅ Grafica guardada: {FEATURE_IMPORTANCE_PATH}")
    
    # Mostrar top 10
    print(f"\n🏆 Top 10 Features mas importantes:")
    for idx, row in feature_importance_df.head(10).iterrows():
        print(f"   {row['feature']:35s}: {row['importance']:.4f}")
    
    return feature_importance_df


def guardar_modelo(modelo, metricas):
    """Serializa el modelo y sus metricas."""
    print(f"\n💾 Guardando modelo...")
    
    modelo_data = {
        'modelo': modelo,
        'metricas_cv': metricas['cv'],
        'metricas_full': metricas['full'],
        'version': '1.0',
        'fecha_entrenamiento': pd.Timestamp.now().isoformat(),
        'n_features': 24
    }
    
    with open(MODEL_OUTPUT_PATH, 'wb') as f:
        pickle.dump(modelo_data, f)
    
    print(f"✅ Modelo guardado: {MODEL_OUTPUT_PATH}")


def main():
    print("="*60)
    print("🚀 ENTRENAMIENTO MODELO XGBOOST - 24 FEATURES")
    print("="*60)
    
    # 1. Cargar datos
    X, y, feature_cols = cargar_datos()
    
    # 2. Entrenar modelo
    modelo = entrenar_modelo(X, y)
    
    # 3. Validacion cruzada
    metricas_cv = validacion_cruzada(modelo, X, y)
    
    # 4. Evaluacion completa
    metricas_full = evaluar_modelo_completo(modelo, X, y)
    
    # 5. Feature importance
    feature_importance_df = graficar_feature_importance(modelo, feature_cols)
    
    # 6. Guardar modelo
    metricas = {
        'cv': metricas_cv,
        'full': metricas_full
    }
    guardar_modelo(modelo, metricas)
    
    print("\n" + "="*60)
    print("✅ ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
    print("="*60)
    print(f"\n📋 Resumen:")
    print(f"   Modelo: XGBoost Regressor")
    print(f"   Features: 24")
    print(f"   Samples: {len(X)}")
    print(f"   MAE (CV): {metricas_cv['mae_mean']:.4f} Bs/kg")
    print(f"   R² (CV): {metricas_cv['r2_mean']:.4f}")
    print(f"\n📁 Archivos generados:")
    print(f"   - {MODEL_OUTPUT_PATH}")
    print(f"   - {FEATURE_IMPORTANCE_PATH}")


if __name__ == "__main__":
    main()
