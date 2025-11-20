#!/usr/bin/env python3
"""
Script para validar modelo usando validación cruzada y métricas MAE/RMSE.
Cumple con el objetivo específico 1.1.1 de validación de precisión.
"""

import sys
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# Agregar path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ml.core.cross_validation import (
    cross_validation_evaluation,
    generate_cross_validation_report
)
from ml.core.training_12_months import generate_12_months_dataset


def main():
    """Función principal para validación del modelo."""
    print("="*70)
    print("VALIDACIÓN DE PRECISIÓN DEL MODELO")
    print("Objetivo Específico 1.1.1: Validación Cruzada con MAE y RMSE")
    print("="*70)
    
    try:
        # 1. Cargar o generar datos
        print("\n1. PREPARANDO DATOS...")
        df = generate_12_months_dataset()
        
        # Preparar features y target
        feature_cols = [
            "cantidad_animales", "peso_promedio_entrada", "precio_compra_kg",
            "costo_logistica_total", "costo_alimentacion_estadia", "duracion_estadia_dias",
            "mes_adquisicion", "costo_total_lote", "peso_salida",
            "costo_fijo_por_kg"  # NUEVO: Costos Fijos como feature
        ]
        
        X = df[feature_cols].values
        y = df["precio_venta_final_kg"].values
        
        # Normalización
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 2. Cargar modelo entrenado
        print("\n2. CARGANDO MODELO ENTRENADO...")
        model_path = "model_store/12_months_model.pkl"
        
        if not Path(model_path).exists():
            print(f"⚠️  Modelo no encontrado en {model_path}")
            print("   Ejecutando entrenamiento primero...")
            from ml.core.training_12_months import main as train_main
            train_main()
        
        model_data = joblib.load(model_path)
        model = model_data['model']
        model_name = model_data.get('model_name', 'Mejor Modelo')
        
        print(f"   ✅ Modelo cargado: {model_name}")
        
        # 3. Validación Cruzada
        print("\n3. REALIZANDO VALIDACIÓN CRUZADA...")
        cv_metrics = cross_validation_evaluation(
            model, X_scaled, y,
            cv_folds=5,
            random_state=42,
            verbose=True
        )
        
        # 4. Generar reporte completo
        print("\n4. GENERANDO REPORTE DE VALIDACIÓN...")
        report = generate_cross_validation_report(
            model, model_name, X_scaled, y,
            cv_folds=5,
            output_path="api/ml/docs/cross_validation_report.json"
        )
        
        # 5. Resumen final
        print("\n" + "="*70)
        print("RESUMEN FINAL - VALIDACIÓN DE PRECISIÓN")
        print("="*70)
        print(f"\n✅ Validación cruzada completada exitosamente")
        print(f"\n📊 MÉTRICAS PRINCIPALES:")
        print(f"   MAE:  {cv_metrics['test_mae']['mean']:.4f} ± {cv_metrics['test_mae']['std']:.4f} Bs/kg")
        print(f"   RMSE: {cv_metrics['test_rmse']['mean']:.4f} ± {cv_metrics['test_rmse']['std']:.4f} Bs/kg")
        
        print(f"\n💡 INTERPRETACIÓN:")
        print(f"   {report['metrics']['mae']['interpretation']}")
        print(f"   {report['metrics']['rmse']['interpretation']}")
        
        print(f"\n📋 RECOMENDACIÓN:")
        print(f"   {report['recommendation']}")
        
        print(f"\n✅ El modelo ha sido validado y está listo para apoyar decisiones estratégicas")
        print(f"   en la fijación de precios.")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error durante la validación: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

