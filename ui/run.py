#!/usr/bin/env python3
"""
Script para ejecutar la aplicación Streamlit
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    # Obtener el directorio actual
    ui_dir = Path(__file__).parent
    
    # Cambiar al directorio ui
    os.chdir(ui_dir)
    
    # Ejecutar streamlit
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app.py",
        "--server.port=8501",
        "--server.address=0.0.0.0"
    ])

if __name__ == "__main__":
    main()



