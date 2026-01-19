#!/usr/bin/env python3
"""
SISTEMA ML CONSOLIDADO V2 - MOTOR XGBOOST
Orquestador para el modelo de alta complejidad (24 features)

Uso:
    python ml_system.py train --n-samples 2000
    python ml_system.py evaluate
    python ml_system.py feature-importance
    python ml_system.py test
"""

import os
import sys
import argparse
from pathlib import Path


def main():
    """Funcion principal del sistema ML actualizado."""
    
    parser = argparse.ArgumentParser(
        description='Motor Predictivo Granja del Cerdo - XGBoost',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python ml_system.py train --n-samples 2000    # Entrenar modelo con 2000 muestras
  python ml_system.py evaluate                  # Evaluar modelo existente
  python ml_system.py feature-importance        # Generar grafica de importancia
  python ml_system.py test                      # Ejecutar pruebas de integracion
        """
    )
    
    parser.add_argument(
        'action', 
        choices=['train', 'evaluate', 'feature-importance', 'test'], 
        help='Accion a ejecutar'
    )
    parser.add_argument(
        '--n-samples', 
        type=int, 
        default=2000, 
        help='Cantidad de datos para entrenamiento (default: 2000)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  SISTEMA DE INTELIGENCIA DE NEGOCIO - GRANJA DEL CERDO")
    print("  Algoritmo: Extreme Gradient Boosting (XGBoost)")
    print("  Features: 24 variables | Modelo: v1.0")
    print("=" * 60)
    print()
    
    try:
        if args.action == 'train':
            print(f"🚀 Iniciando entrenamiento con {args.n_samples} muestras...")
            print()
            
            # Paso 1: Generar dataset sintetico
            print("📊 Paso 1/2: Generando dataset sintetico...")
            from ml.data.generate_data import main as generate_main
            sys.argv = ['generate_data.py', '--n', str(args.n_samples)]
            generate_main()
            
            print()
            print("🤖 Paso 2/2: Entrenando modelo XGBoost...")
            # Paso 2: Entrenar modelo
            from ml.train_xgboost import main as train_main
            train_main()

        elif args.action == 'evaluate':
            print("📊 Evaluando precision del modelo (MAE, RMSE, R²)...")
            print()
            
            # Agregar path para imports
            sys.path.insert(0, str(Path(__file__).parent))
            
            import pickle
            from train_xgboost import cargar_datos, evaluar_modelo_completo
            
            model_path = Path('ml/models/xgboost_24_features.pkl')
            if not model_path.exists():
                print(f"❌ Error: Modelo no encontrado en {model_path}")
                print("   Ejecuta primero: python ml_system.py train")
                sys.exit(1)
            
            with open(model_path, 'rb') as f:
                data = pickle.load(f)
            
            X, y, _ = cargar_datos()
            metricas = evaluar_modelo_completo(data['modelo'], X, y)
            
            print()
            print("📋 Metricas de Validacion Cruzada:")
            print(f"   MAE:  {data['metricas_cv']['mae_mean']:.4f} ± {data['metricas_cv']['mae_std']:.4f} Bs/kg")
            print(f"   RMSE: {data['metricas_cv']['rmse_mean']:.4f} ± {data['metricas_cv']['rmse_std']:.4f} Bs/kg")
            print(f"   R²:   {data['metricas_cv']['r2_mean']:.4f} ± {data['metricas_cv']['r2_std']:.4f}")
    
        elif args.action == 'feature-importance':
            print("🏆 Generando analisis de importancia de variables...")
            print()
            
            # Agregar path para imports
            sys.path.insert(0, str(Path(__file__).parent))
            
            import pickle
            from train_xgboost import graficar_feature_importance, cargar_datos
            
            model_path = Path('ml/models/xgboost_24_features.pkl')
            if not model_path.exists():
                print(f"❌ Error: Modelo no encontrado en {model_path}")
                print("   Ejecuta primero: python ml_system.py train")
                sys.exit(1)
            
            with open(model_path, 'rb') as f:
                data = pickle.load(f)
            
            X, _, feature_cols = cargar_datos()
            graficar_feature_importance(data['modelo'], feature_cols)

        elif args.action == 'test':
            print("🧪 Ejecutando pruebas de integracion con prorrateo dinamico...")
            print()
            
            # Agregar path para importar db
            sys.path.insert(0, str(Path(__file__).parent.parent))
            
            # Verificar que existan los datos necesarios
            import asyncio
            from db import db
            
            async def verificar_datos():
                await db.connect()
                try:
                    # Verificar feriados
                    feriados = await db.feriado.count()
                    print(f"✅ Feriados en BD: {feriados}")
                    
                    # Verificar gastos mensuales
                    gastos = await db.gastomensual.count()
                    print(f"✅ Gastos mensuales en BD: {gastos}")
                    
                    # Verificar tipos de costo
                    tipos = await db.tipocosto.count()
                    print(f"✅ Tipos de costo en BD: {tipos}")
                    
                    if feriados == 0 or gastos == 0 or tipos == 0:
                        print()
                        print("⚠️  Advertencia: Faltan datos en la BD")
                        print("   Ejecuta: python poblar_feriados.py")
                        print("   Ejecuta: python poblar_gastos_mensuales.py")
                    else:
                        print()
                        print("✅ Todos los datos necesarios estan presentes")
                        
                finally:
                    await db.disconnect()
            
            asyncio.run(verificar_datos())
    
        print()
        print("=" * 60)
        print("✅ Operacion finalizada exitosamente")
        print("=" * 60)
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Error durante la ejecucion: {str(e)}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
