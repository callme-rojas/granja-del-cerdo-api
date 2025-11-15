#!/usr/bin/env python3
"""
SCRIPT DE PRUEBAS RÁPIDAS - API BACKEND + ML
Versión simplificada para pruebas rápidas y validación básica
"""

import requests
import json
from datetime import datetime

class QuickAPITest:
    """Pruebas rápidas de la API."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.token = None
    
    def authenticate(self) -> bool:
        """Autenticación rápida."""
        print("Autenticando...")
        
        login_data = {
            "email": "dayanadelgadillo@granja.com",
            "password": "granjacerdo"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/v1/login", json=login_data)
            if response.status_code == 200:
                auth_response = response.json()
                self.token = auth_response.get('access_token')
                if self.token:
                    self.session.headers.update({'Authorization': f'Bearer {self.token}'})
                    print("Autenticacion exitosa")
                    return True
            print(f"Error de autenticacion: {response.status_code}")
            return False
        except Exception as e:
            print(f"Error: {str(e)}")
            return False
    
    def test_ml_prediction(self) -> bool:
        """Prueba rápida de predicción ML."""
        print("Probando prediccion ML...")
        
        # Crear lote de prueba
        lote_data = {
            "fecha_adquisicion": "2025-01-15",
            "cantidad_animales": 30,
            "peso_promedio_entrada": 95.0,
            "precio_compra_kg": 18.5,
            "duracion_estadia_dias": 3
        }
        
        try:
            # Crear lote
            response = self.session.post(f"{self.base_url}/api/v1/lotes", json=lote_data)
            if response.status_code != 201:
                print(f"Error creando lote: {response.status_code}")
                return False
            
            lote_id = response.json()['id_lote']
            print(f"Lote creado: {lote_id}")
            
            # Agregar costo
            tipos_response = self.session.get(f"{self.base_url}/api/v1/tipos-costo")
            if tipos_response.status_code == 200:
                tipos = tipos_response.json()
                if tipos:
                    costo_data = {
                        "id_tipo_costo": tipos[0]['id_tipo_costo'],
                        "monto": 800.0,
                        "fecha_gasto": "2025-01-15",
                        "descripcion": "Transporte"
                    }
                    
                    costo_response = self.session.post(f"{self.base_url}/api/v1/lotes/{lote_id}/costos", json=costo_data)
                    if costo_response.status_code == 201:
                        print("Costo agregado")
            
            # Agregar producción
            produccion_data = {
                "peso_salida_total": 2800.0,
                "mortalidad_unidades": 1
            }
            
            prod_response = self.session.post(f"{self.base_url}/api/v1/lotes/{lote_id}/produccion", json=produccion_data)
            if prod_response.status_code == 201:
                print("Produccion agregada")
            
            # Hacer predicción
            prediction_response = self.session.post(f"{self.base_url}/api/v1/lotes/predict", json={"id_lote": lote_id})
            if prediction_response.status_code == 200:
                prediction = prediction_response.json()
                print("Prediccion ML exitosa:")
                print(f"   Precio base: {prediction.get('precio_base_kg', 'N/A'):.4f} Bs/kg")
                print(f"   Precio sugerido: {prediction.get('precio_sugerido_kg', 'N/A'):.4f} Bs/kg")
                print(f"   Ganancia neta: {prediction.get('ganancia_neta_estimada', 'N/A'):.2f} Bs")
                print(f"   Margen: {prediction.get('margen_rate', 'N/A')*100:.1f}%")
                
                # Probar margen dinámico
                dynamic_response = self.session.post(f"{self.base_url}/api/v1/lotes/predict", 
                                                   json={"id_lote": lote_id, "margen_rate": 0.12})
                if dynamic_response.status_code == 200:
                    dynamic_pred = dynamic_response.json()
                    print(f"Margen dinamico (12%): {dynamic_pred.get('precio_sugerido_kg', 'N/A'):.4f} Bs/kg")
                
                # Limpiar
                self.session.delete(f"{self.base_url}/api/v1/lotes/{lote_id}")
                print("Lote eliminado")
                
                return True
            else:
                print(f"Error en prediccion: {prediction_response.status_code}")
                print(f"   {prediction_response.text}")
                return False
                
        except Exception as e:
            print(f"Error: {str(e)}")
            return False
    
    def run_quick_test(self) -> bool:
        """Ejecuta prueba rápida completa."""
        print("PRUEBA RAPIDA API + ML")
        print("=" * 40)
        
        if not self.authenticate():
            return False
        
        if not self.test_ml_prediction():
            return False
        
        print("\nPRUEBA RAPIDA COMPLETADA EXITOSAMENTE")
        return True

def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Prueba Rápida API Backend + ML')
    parser.add_argument('--url', default='http://127.0.0.1:8000', help='URL del backend')
    
    args = parser.parse_args()
    
    test = QuickAPITest(args.url)
    success = test.run_quick_test()
    
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
