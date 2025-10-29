#!/usr/bin/env python3
"""
SISTEMA ML CONSOLIDADO - ENTRENAMIENTO Y PREDICCIÓN
Script principal para entrenar modelos y hacer predicciones
"""

import os
import sys
import argparse
from pathlib import Path

def main():
    """Función principal del sistema ML."""
    
    parser = argparse.ArgumentParser(description='Sistema ML Consolidado')
    parser.add_argument('action', choices=['train', 'compare', 'evaluate', 'test'], 
                       help='Acción a ejecutar')
    parser.add_argument('--dataset-size', type=int, default=360, 
                       help='Tamaño del dataset (default: 360)')
    parser.add_argument('--model-type', choices=['12months', '3algorithms'], 
                       default='12months', help='Tipo de modelo a entrenar')
    
    args = parser.parse_args()
    
    print("SISTEMA ML CONSOLIDADO")
    print("=" * 30)
    
    if args.action == 'train':
        if args.model_type == '12months':
            print("Entrenando modelo de 12 meses...")
            from core.training_12_months import main as train_12_months
            train_12_months()
        else:
            print("Entrenando comparación de 3 algoritmos...")
            from core.compare_models import compare_models
            compare_models()
    
    elif args.action == 'compare':
        print("Comparando algoritmos...")
        from core.compare_models import compare_models
        compare_models()
    
    elif args.action == 'evaluate':
        print("Evaluando modelo...")
        from core.evaluate_model import main as evaluate_main
        evaluate_main()
    
    elif args.action == 'test':
        print("Probando integración...")
        from tests.test_integration import create_test_lote_manual
        create_test_lote_manual()
    
    print("\nAcción completada exitosamente!")

if __name__ == "__main__":
    main()
