#!/usr/bin/env python3
"""
Script maestro para ejecutar todo el pipeline de ML:
1. Generar datos sintéticos
2. Entrenar modelo
3. Evaluar modelo
4. Validar integración con backend
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd: str, description: str) -> bool:
    """Ejecuta un comando y maneja errores."""
    print(f"\n{description}")
    print(f"Ejecutando: {cmd}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Warnings: {result.stderr}")
        print(f"{description} completado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error en {description}:")
        print(f"Exit code: {e.returncode}")
        print(f"Error: {e.stderr}")
        return False

def check_requirements():
    """Verifica que las dependencias estén instaladas."""
    required_packages = ['numpy', 'pandas', 'sklearn', 'joblib']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Paquetes faltantes: {missing_packages}")
        print("Instala con: pip install numpy pandas scikit-learn joblib")
        return False
    
    print("Todas las dependencias están instaladas")
    return True

def main():
    """Función principal del pipeline."""
    parser = argparse.ArgumentParser(description="Pipeline completo de ML para reventa de cerdos")
    parser.add_argument("--n", type=int, default=2000, help="número de lotes sintéticos a generar")
    parser.add_argument("--skip-data", action="store_true", help="saltar generación de datos")
    parser.add_argument("--skip-train", action="store_true", help="saltar entrenamiento")
    parser.add_argument("--skip-eval", action="store_true", help="saltar evaluación")
    args = parser.parse_args()
    
    print("PIPELINE COMPLETO DE ML - REVENTA DE CERDOS")
    print("=" * 60)
    print(f"Lotes a generar: {args.n}")
    print(f"Directorio de trabajo: {os.getcwd()}")
    
    # Verificar dependencias
    if not check_requirements():
        return 1
    
    # Cambiar al directorio correcto
    ml_dir = Path(".")
    if not ml_dir.exists():
        print(f"Directorio ML no encontrado: {ml_dir}")
        return 1
    
    os.chdir(ml_dir)
    print(f"Cambiado a directorio: {os.getcwd()}")
    
    success_count = 0
    total_steps = 3
    
    # Paso 1: Generar datos sintéticos
    if not args.skip_data:
        cmd = f"python data/generate_data.py --n {args.n}"
        if run_command(cmd, "Generación de datos sintéticos"):
            success_count += 1
    else:
        print("Saltando generación de datos")
        success_count += 1
    
    # Paso 2: Entrenar modelo
    if not args.skip_train:
        cmd = "python train_model.py"
        if run_command(cmd, "Entrenamiento del modelo"):
            success_count += 1
    else:
        print("Saltando entrenamiento")
        success_count += 1
    
    # Paso 3: Evaluar modelo
    if not args.skip_eval:
        cmd = "python evaluate_model.py"
        if run_command(cmd, "Evaluación del modelo"):
            success_count += 1
    else:
        print("Saltando evaluación")
        success_count += 1
    
    # Resumen final
    print(f"\nPIPELINE COMPLETADO")
    print("=" * 60)
    print(f"Pasos exitosos: {success_count}/{total_steps}")
    
    if success_count == total_steps:
        print("¡Pipeline completado exitosamente!")
        print("El modelo está listo para usar en el backend")
        
        # Verificar archivos generados
        model_path = Path("model_store/latest.pkl")
        data_path = Path("data/synthetic_features.csv")
        
        if model_path.exists() and data_path.exists():
            print(f"Modelo: {model_path}")
            print(f"Datos: {data_path}")
            print("\nPara probar el backend:")
            print("   1. Inicia el servidor: cd ../.. && python api/app.py")
            print("   2. Prueba el endpoint: POST /api/v1/lotes/predict")
        else:
            print("Algunos archivos no se generaron correctamente")
        
        return 0
    else:
        print("Pipeline falló en algunos pasos")
        return 1

if __name__ == "__main__":
    exit(main())
