#!/usr/bin/env python3
"""
SCRIPT DE PRUEBA PARA INTEGRACIÓN CON BACKEND
Prueba el modelo entrenado con un lote real
"""

import requests
import json
import pandas as pd
from datetime import datetime

def test_backend_integration():
    """Prueba la integración del modelo ML con el backend."""
    
    print("PRUEBA DE INTEGRACION CON BACKEND")
    print("=" * 50)
    
    # URL del backend (ajustar según tu configuración)
    base_url = "http://localhost:5000"
    
    # 1. Crear un lote de prueba
    print("\n1. Creando lote de prueba...")
    
    lote_data = {
        "fecha_adquisicion": "2025-01-15",
        "cantidad_animales": 25,
        "peso_promedio_entrada": 95.5,
        "precio_compra_kg": 19.2,
        "duracion_estadia_dias": 2
    }
    
    try:
        # Crear lote
        response = requests.post(f"{base_url}/api/v1/lotes", json=lote_data)
        if response.status_code == 201:
            lote = response.json()
            lote_id = lote['id']
            print(f"Lote creado exitosamente: ID {lote_id}")
        else:
            print(f"Error creando lote: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return
    except requests.exceptions.ConnectionError:
        print("Error: No se puede conectar al backend")
        print("Asegurate de que el servidor Flask este ejecutandose")
        return
    
    # 2. Agregar costos al lote
    print("\n2. Agregando costos al lote...")
    
    costos_data = [
        {
            "id_lote": lote_id,
            "id_tipo_costo": 1,  # Asumiendo que existe tipo costo con ID 1
            "monto": 650.0,
            "fecha": "2025-01-15",
            "descripcion": "Costo logistica"
        },
        {
            "id_lote": lote_id,
            "id_tipo_costo": 2,  # Asumiendo que existe tipo costo con ID 2
            "monto": 50.0,
            "fecha": "2025-01-15",
            "descripcion": "Costo alimentacion"
        }
    ]
    
    for costo in costos_data:
        try:
            response = requests.post(f"{base_url}/api/v1/costos", json=costo)
            if response.status_code == 201:
                print(f"Costo agregado: {costo['descripcion']}")
            else:
                print(f"Error agregando costo: {response.status_code}")
        except Exception as e:
            print(f"Error agregando costo: {e}")
    
    # 3. Obtener features del lote
    print("\n3. Obteniendo features del lote...")
    
    try:
        response = requests.get(f"{base_url}/api/features/lote/{lote_id}")
        if response.status_code == 200:
            features = response.json()
            print("Features obtenidas exitosamente:")
            print(json.dumps(features, indent=2))
        else:
            print(f"Error obteniendo features: {response.status_code}")
            return
    except Exception as e:
        print(f"Error obteniendo features: {e}")
        return
    
    # 4. Hacer predicción ML
    print("\n4. Haciendo prediccion ML...")
    
    try:
        response = requests.post(f"{base_url}/api/v1/prediccion", json={"id_lote": lote_id})
        if response.status_code == 200:
            prediccion = response.json()
            print("Prediccion exitosa:")
            print(json.dumps(prediccion, indent=2))
            
            # Mostrar resultados clave
            print(f"\nRESULTADOS CLAVE:")
            print(f"- Precio sugerido: {prediccion.get('precio_sugerido_kg', 'N/A')} Bs/kg")
            print(f"- Ganancia neta estimada: {prediccion.get('ganancia_neta_estimada', 'N/A')} Bs")
            print(f"- Modelo usado: {prediccion.get('modelo_usado', 'N/A')}")
            
        else:
            print(f"Error en prediccion: {response.status_code}")
            print(f"Respuesta: {response.text}")
    except Exception as e:
        print(f"Error en prediccion: {e}")
    
    # 5. Crear reporte de prueba
    print("\n5. Creando reporte de prueba...")
    
    reporte = {
        "timestamp": datetime.now().isoformat(),
        "lote_prueba": lote_data,
        "costos_agregados": costos_data,
        "features_obtenidas": features if 'features' in locals() else None,
        "prediccion_resultado": prediccion if 'prediccion' in locals() else None,
        "estado": "Prueba completada"
    }
    
    # Guardar reporte
    with open("prueba_integracion.json", "w") as f:
        json.dump(reporte, f, indent=2)
    
    print("Reporte de prueba guardado: prueba_integracion.json")
    print("\nPrueba de integracion completada!")

def create_test_lote_manual():
    """Crea un lote de prueba manual para análisis."""
    
    print("\nCREANDO LOTE DE PRUEBA MANUAL")
    print("=" * 40)
    
    # Datos del lote de prueba
    lote_prueba = {
        "fecha_adquisicion": "2025-01-15",
        "cantidad_animales": 30,
        "peso_promedio_entrada": 98.5,
        "precio_compra_kg": 18.8,
        "duracion_estadia_dias": 2,
        "costos": [
            {"tipo": "logistica", "monto": 720.0},
            {"tipo": "alimentacion", "monto": 60.0}
        ]
    }
    
    # Calcular features manualmente
    kilos_entrada = lote_prueba["cantidad_animales"] * lote_prueba["peso_promedio_entrada"]
    kilos_salida = kilos_entrada * 1.01  # +1% variación
    
    costo_logistica = 720.0
    costo_alimentacion = 60.0
    costo_total_lote = (kilos_entrada * lote_prueba["precio_compra_kg"]) + costo_logistica + costo_alimentacion
    
    features = {
        "cantidad_animales": lote_prueba["cantidad_animales"],
        "peso_promedio_entrada": lote_prueba["peso_promedio_entrada"],
        "precio_compra_kg": lote_prueba["precio_compra_kg"],
        "costo_logistica": costo_logistica,
        "costo_alimentacion": costo_alimentacion,
        "duracion_estadia_dias": lote_prueba["duracion_estadia_dias"],
        "mes_adquisicion": 1,  # Enero
        "costo_total_lote": costo_total_lote,
        "peso_salida": kilos_salida
    }
    
    print("Lote de prueba creado:")
    print(json.dumps(lote_prueba, indent=2))
    print("\nFeatures calculadas:")
    print(json.dumps(features, indent=2))
    
    # Guardar lote de prueba
    with open("lote_prueba_manual.json", "w") as f:
        json.dump({
            "lote": lote_prueba,
            "features": features,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)
    
    print("\nLote de prueba guardado: lote_prueba_manual.json")
    
    return features

if __name__ == "__main__":
    print("SELECCIONA UNA OPCION:")
    print("1. Probar integracion con backend (requiere servidor Flask)")
    print("2. Crear lote de prueba manual")
    
    opcion = input("Ingresa opcion (1 o 2): ").strip()
    
    if opcion == "1":
        test_backend_integration()
    elif opcion == "2":
        create_test_lote_manual()
    else:
        print("Opcion invalida")
