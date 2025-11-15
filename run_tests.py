#!/usr/bin/env python3
"""
SCRIPT DE PRUEBAS UNITARIAS - API BACKEND + ML
Ejecuta las pruebas desde la raíz del proyecto
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """Función principal para ejecutar pruebas."""
    
    # Verificar que estamos en la raíz del proyecto
    if not Path("api").exists():
        print("Error: Ejecutar desde la raiz del proyecto (donde esta la carpeta 'api')")
        sys.exit(1)
    
    # Verificar que el backend esté ejecutándose
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code != 200:
            print("Error: Backend no esta ejecutandose en http://127.0.0.1:8000")
            print("   Inicia el backend con: python api/app.py")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Error: No se puede conectar al backend en http://127.0.0.1:8000")
        print("   Inicia el backend con: python api/app.py")
        sys.exit(1)
    except ImportError:
        print("Error: Instala requests: pip install requests")
        sys.exit(1)
    
    # Mostrar opciones
    print("PRUEBAS UNITARIAS - API BACKEND + ML")
    print("=" * 50)
    print("1. Prueba Rapida (recomendada para demostracion)")
    print("2. Suite Completa (todas las pruebas)")
    print("3. Prueba de Margenes Dinamicos")
    print("4. Prueba de Integracion con Auth")
    print("5. Salir")
    print("=" * 50)
    
    # Si se pasa un argumento, usar ese directamente
    if len(sys.argv) > 1:
        opcion = sys.argv[1]
    else:
        try:
            opcion = input("\nSelecciona una opcion (1-5): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHasta luego!")
            sys.exit(0)
    
    try:
        if opcion == "1":
            print("\nEjecutando Prueba Rapida...")
            subprocess.run([sys.executable, "api/ml/tests/test_rapido.py"], check=True)
            
        elif opcion == "2":
            print("\nEjecutando Suite Completa...")
            subprocess.run([sys.executable, "api/ml/tests/test_suite_completa.py"], check=True)
            
        elif opcion == "3":
            print("\nEjecutando Prueba de Margenes Dinamicos...")
            subprocess.run([sys.executable, "api/ml/tests/test_dynamic_margins.py"], check=True)
            
        elif opcion == "4":
            print("\nEjecutando Prueba de Integracion con Auth...")
            subprocess.run([sys.executable, "api/ml/tests/test_integration_auth.py"], check=True)
            
        elif opcion == "5":
            print("Hasta luego!")
            sys.exit(0)
            
        else:
            print("Opcion invalida. Selecciona 1-5.")
            print("\nUso:")
            print("  python run_tests.py [1-5]")
            print("  python run_tests.py 1    # Prueba rapida")
            print("  python run_tests.py 2    # Suite completa")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nHasta luego!")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando prueba: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
