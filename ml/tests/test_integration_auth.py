#!/usr/bin/env python3
"""
INTEGRACION CON BACKEND Y AUTENTICACION JWT
Prueba la integracion del modelo ML con el backend Flask
Backend URL: http://127.0.0.1:8000
"""

import requests
import json
import time
from datetime import datetime

class BackendIntegrationWithAuth:
    """Clase para manejar la integracion con el backend incluyendo autenticacion."""
    
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.token = None
    
    def login(self, email="dayanadelgadillo@granja.com", password="granjacerdo"):
        """Autentica con el backend y obtiene el token JWT."""
        print("AUTENTICANDO CON BACKEND")
        print("=" * 30)
        
        login_data = {
            "email": email,
            "password": password
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/v1/login", json=login_data)
            if response.status_code == 200:
                auth_response = response.json()
                self.token = auth_response.get('access_token')
                if self.token:
                    # Agregar token a los headers
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.token}'
                    })
                    print("OK Autenticacion exitosa")
                    print(f"Token obtenido: {self.token[:20]}...")
                    return True
                else:
                    print("ERROR: No se obtuvo token en la respuesta")
                    return False
            else:
                print(f"ERROR en autenticacion: {response.status_code}")
                print(f"Respuesta: {response.text}")
                return False
        except Exception as e:
            print(f"ERROR en autenticacion: {e}")
            return False
    
    def test_connection(self):
        """Prueba la conexion con el backend."""
        print("PRUEBA DE CONEXION CON BACKEND")
        print("=" * 40)
        print(f"URL: {self.base_url}")
        
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                print("OK Backend conectado exitosamente")
                print(f"Respuesta: {response.text[:200]}...")
                return True
            else:
                print(f"ERROR en backend: {response.status_code}")
                print(f"Respuesta: {response.text}")
                return False
        except requests.exceptions.ConnectionError:
            print("ERROR: No se puede conectar al backend")
            print("Asegurate de que el servidor Flask este ejecutandose en puerto 8000")
            return False
        except Exception as e:
            print(f"ERROR inesperado: {e}")
            return False
    
    def create_test_lote(self):
        """Crea un lote de prueba en el backend."""
        print("\nCREANDO LOTE DE PRUEBA")
        print("=" * 30)
        
        lote_data = {
            "fecha_adquisicion": "2025-01-15",
            "cantidad_animales": 30,
            "peso_promedio_entrada": 98.5,
            "precio_compra_kg": 18.8,
            "duracion_estadia_dias": 2
        }
        
        print("Datos del lote:")
        print(json.dumps(lote_data, indent=2))
        
        try:
            response = self.session.post(f"{self.base_url}/api/v1/lotes", json=lote_data)
            print(f"Status code: {response.status_code}")
            print(f"Respuesta completa: {response.text}")
            
            if response.status_code == 201:
                lote = response.json()
                print(f"Lote creado: {lote}")
                
                # Buscar el ID en diferentes campos posibles
                lote_id = lote.get('id') or lote.get('id_lote') or lote.get('lote_id') or lote.get('loteId')
                if lote_id:
                    print(f"OK Lote creado exitosamente: ID {lote_id}")
                    return lote_id
                else:
                    print(f"ERROR: No se encontro ID en la respuesta")
                    print(f"Campos disponibles: {list(lote.keys())}")
                    return None
            else:
                print(f"ERROR creando lote: {response.status_code}")
                print(f"Respuesta: {response.text}")
                return None
        except Exception as e:
            print(f"ERROR creando lote: {e}")
            return None
    
    def get_tipos_costo(self):
        """Obtiene los tipos de costo disponibles."""
        print("\nOBTENIENDO TIPOS DE COSTO")
        print("=" * 30)
        
        try:
            response = self.session.get(f"{self.base_url}/api/v1/tipos-costo")
            if response.status_code == 200:
                tipos_costo = response.json()
                print(f"OK Tipos de costo obtenidos: {len(tipos_costo)}")
                print(f"Respuesta completa: {json.dumps(tipos_costo, indent=2)}")
                
                # Verificar estructura de datos
                if tipos_costo and len(tipos_costo) > 0:
                    first_tipo = tipos_costo[0]
                    print(f"Primer tipo: {first_tipo}")
                    print(f"Campos disponibles: {list(first_tipo.keys())}")
                
                return tipos_costo
            else:
                print(f"ERROR obteniendo tipos de costo: {response.status_code}")
                print(f"Respuesta: {response.text}")
                return []
        except Exception as e:
            print(f"ERROR obteniendo tipos de costo: {e}")
            return []
    
    def add_test_costs(self, lote_id, tipos_costo):
        """Agrega costos de prueba al lote."""
        print(f"\nAGREGANDO COSTOS AL LOTE {lote_id}")
        print("=" * 40)
        
        if not tipos_costo:
            print("ERROR: No hay tipos de costo disponibles")
            return False
        
        # Buscar tipos especificos o usar los primeros disponibles
        tipo_logistica_id = None
        tipo_alimentacion_id = None
        
        for tipo in tipos_costo:
            if 'logistica' in tipo.get('nombre_tipo', '').lower():
                tipo_logistica_id = tipo['id_tipo_costo']
            elif 'alimentacion' in tipo.get('nombre_tipo', '').lower():
                tipo_alimentacion_id = tipo['id_tipo_costo']
        
        # Si no encontramos tipos especificos, usar los primeros disponibles
        if not tipo_logistica_id and tipos_costo:
            tipo_logistica_id = tipos_costo[0]['id_tipo_costo']
        if not tipo_alimentacion_id and len(tipos_costo) > 1:
            tipo_alimentacion_id = tipos_costo[1]['id_tipo_costo']
        elif not tipo_alimentacion_id and tipos_costo:
            tipo_alimentacion_id = tipos_costo[0]['id_tipo_costo']
        
        print(f"Usando tipo logistica ID: {tipo_logistica_id}")
        print(f"Usando tipo alimentacion ID: {tipo_alimentacion_id}")
        
        # Agregar costos (usar endpoint: POST /api/v1/lotes/{id}/costos)
        costos_data = [
            {
                "id_tipo_costo": tipo_logistica_id,
                "monto": 720.0,
                "fecha_gasto": "2025-01-15",
                "descripcion": "Costo logistica - Transporte"
            },
            {
                "id_tipo_costo": tipo_alimentacion_id,
                "monto": 60.0,
                "fecha_gasto": "2025-01-15",
                "descripcion": "Costo alimentacion - 2 dias"
            }
        ]
        
        success_count = 0
        for costo in costos_data:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/v1/lotes/{lote_id}/costos",
                    json=costo,
                )
                if response.status_code == 201:
                    print(f"OK Costo agregado: {costo['descripcion']}")
                    success_count += 1
                else:
                    print(f"ERROR agregando costo: {response.status_code}")
                    print(f"Respuesta: {response.text}")
            except Exception as e:
                print(f"ERROR agregando costo: {e}")
        
        return success_count > 0
    
    def get_lote_features(self, lote_id):
        """Obtiene las features del lote para el modelo ML."""
        print(f"\nOBTENIENDO FEATURES DEL LOTE {lote_id}")
        print("=" * 40)
        
        try:
            response = self.session.get(f"{self.base_url}/api/v1/lotes/{lote_id}/features")
            if response.status_code == 200:
                features = response.json()
                print("OK Features obtenidas exitosamente:")
                print(json.dumps(features, indent=2))
                return features
            else:
                print(f"ERROR obteniendo features: {response.status_code}")
                print(f"Respuesta: {response.text}")
                return None
        except Exception as e:
            print(f"ERROR obteniendo features: {e}")
            return None
    
    def make_ml_prediction(self, lote_id):
        """Hace una prediccion ML usando el lote."""
        print(f"\nHACIENDO PREDICCION ML PARA LOTE {lote_id}")
        print("=" * 45)
        
        try:
            response = self.session.post(f"{self.base_url}/api/v1/lotes/predict", json={"id_lote": lote_id})
            if response.status_code == 200:
                prediccion = response.json()
                print("OK Prediccion exitosa:")
                print(json.dumps(prediccion, indent=2))
                
                # Mostrar resultados clave
                print(f"\nRESULTADOS CLAVE:")
                print(f"- Precio sugerido: {prediccion.get('precio_sugerido_kg', 'N/A')} Bs/kg")
                print(f"- Ganancia neta estimada: {prediccion.get('ganancia_neta_estimada', 'N/A')} Bs")
                print(f"- Modelo usado: {prediccion.get('modelo_usado', 'N/A')}")
                
                return prediccion
            else:
                print(f"ERROR en prediccion: {response.status_code}")
                print(f"Respuesta: {response.text}")
                return None
        except Exception as e:
            print(f"ERROR en prediccion: {e}")
            return None
    
    def run_complete_test(self):
        """Ejecuta la prueba completa de integracion."""
        print("INTEGRACION COMPLETA ML - BACKEND CON AUTENTICACION")
        print("=" * 60)
        
        # 1. Probar conexion
        if not self.test_connection():
            return False
        
        # 2. Autenticar
        if not self.login():
            return False
        
        # 3. Crear lote de prueba
        lote_id = self.create_test_lote()
        if not lote_id:
            return False
        
        # 4. Obtener tipos de costo
        tipos_costo = self.get_tipos_costo()
        
        # 5. Agregar costos
        if tipos_costo:
            self.add_test_costs(lote_id, tipos_costo)
        else:
            print("ADVERTENCIA: Continuando sin costos...")
        
        # 6. Hacer prediccion ML (la API construye las features internamente)
        prediccion = self.make_ml_prediction(lote_id)
        if not prediccion:
            return False
        
        # 7. Guardar resultados
        self.save_test_results(lote_id, None, prediccion)
        
        print(f"\nOK INTEGRACION COMPLETA EXITOSA")
        print(f"Lote ID: {lote_id}")
        print(f"Archivos generados: test_results.json")
        
        return True
    
    def save_test_results(self, lote_id, features, prediccion):
        """Guarda los resultados de la prueba."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "lote_id": lote_id,
            "features": features,
            "prediccion": prediccion,
            "backend_url": self.base_url,
            "token_used": self.token[:20] + "..." if self.token else None,
            "status": "success"
        }
        
        with open("test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"OK Resultados guardados en: test_results.json")

def main():
    """Funcion principal."""
    integration = BackendIntegrationWithAuth()
    success = integration.run_complete_test()
    
    if success:
        print(f"\nINTEGRACION COMPLETA EXITOSA!")
        print(f"El sistema ML esta funcionando correctamente con el backend")
    else:
        print(f"\nERROR en la integracion")
        print(f"Revisa los mensajes de error arriba")

if __name__ == "__main__":
    main()
