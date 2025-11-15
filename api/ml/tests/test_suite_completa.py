#!/usr/bin/env python3
"""
SCRIPT DE PRUEBAS UNITARIAS COMPLETO - API BACKEND + ML
Prueba todos los endpoints de la API y valida el modelo ML
"""

import requests
import json
import time
from datetime import datetime, timedelta
import random
from typing import Dict, List, Optional, Tuple

class APITestSuite:
    """Suite completa de pruebas para la API Backend + ML."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.token = None
        self.test_results = []
        self.created_resources = {
            'lotes': [],
            'costos': [],
            'tipos_costo': [],
            'produccion': [],
            'predicciones': []
        }
    
    def log_test(self, test_name: str, success: bool, details: str = "", data: dict = None):
        """Registra el resultado de una prueba."""
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'data': data or {}
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        if data and not success:
            print(f"    Data: {data}")
    
    def authenticate(self) -> bool:
        """Prueba la autenticación JWT."""
        print("\n🔐 PRUEBA DE AUTENTICACIÓN")
        print("=" * 40)
        
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
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.token}'
                    })
                    self.log_test("Autenticación JWT", True, f"Token obtenido: {self.token[:20]}...")
                    return True
                else:
                    self.log_test("Autenticación JWT", False, "No se obtuvo token en la respuesta")
                    return False
            else:
                self.log_test("Autenticación JWT", False, f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Autenticación JWT", False, f"Error: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """Prueba la conexión básica con el backend."""
        print("\n🌐 PRUEBA DE CONEXIÓN")
        print("=" * 40)
        
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            
            if response.status_code == 200:
                self.log_test("Conexión Backend", True, f"Backend respondiendo en {self.base_url}")
                return True
            else:
                self.log_test("Conexión Backend", False, f"Status {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.log_test("Conexión Backend", False, "No se puede conectar al backend")
            return False
        except Exception as e:
            self.log_test("Conexión Backend", False, f"Error: {str(e)}")
            return False
    
    def test_tipos_costo_crud(self) -> bool:
        """Prueba CRUD completo de tipos de costo."""
        print("\n💰 PRUEBAS CRUD - TIPOS DE COSTO")
        print("=" * 40)
        
        # 1. Listar tipos de costo existentes
        try:
            response = self.session.get(f"{self.base_url}/api/v1/tipos-costo")
            if response.status_code == 200:
                tipos_existentes = response.json()
                self.log_test("Listar Tipos de Costo", True, f"Encontrados {len(tipos_existentes)} tipos")
                
                # Guardar IDs para uso posterior
                for tipo in tipos_existentes:
                    self.created_resources['tipos_costo'].append(tipo['id_tipo_costo'])
            else:
                self.log_test("Listar Tipos de Costo", False, f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Listar Tipos de Costo", False, f"Error: {str(e)}")
            return False
        
        # 2. Crear nuevo tipo de costo
        nuevo_tipo = {
            "nombre_tipo": f"Test Tipo {int(time.time())}",
            "categoria": "VARIABLE"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/v1/tipos-costo", json=nuevo_tipo)
            if response.status_code == 201:
                tipo_creado = response.json()
                tipo_id = tipo_creado['id_tipo_costo']
                self.created_resources['tipos_costo'].append(tipo_id)
                self.log_test("Crear Tipo de Costo", True, f"ID: {tipo_id}")
            else:
                self.log_test("Crear Tipo de Costo", False, f"Status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Crear Tipo de Costo", False, f"Error: {str(e)}")
            return False
        
        # 3. Actualizar tipo de costo
        try:
            update_data = {"nombre_tipo": f"Test Tipo Actualizado {int(time.time())}"}
            response = self.session.patch(f"{self.base_url}/api/v1/tipos-costo/{tipo_id}", json=update_data)
            if response.status_code == 200:
                self.log_test("Actualizar Tipo de Costo", True, f"ID: {tipo_id}")
            else:
                self.log_test("Actualizar Tipo de Costo", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("Actualizar Tipo de Costo", False, f"Error: {str(e)}")
        
        # 4. Eliminar tipo de costo
        try:
            response = self.session.delete(f"{self.base_url}/api/v1/tipos-costo/{tipo_id}")
            if response.status_code == 200:
                self.log_test("Eliminar Tipo de Costo", True, f"ID: {tipo_id}")
                self.created_resources['tipos_costo'].remove(tipo_id)
            else:
                self.log_test("Eliminar Tipo de Costo", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("Eliminar Tipo de Costo", False, f"Error: {str(e)}")
        
        return True
    
    def test_lotes_crud(self) -> bool:
        """Prueba CRUD completo de lotes."""
        print("\n🐷 PRUEBAS CRUD - LOTES")
        print("=" * 40)
        
        # 1. Crear lote de prueba
        lote_data = {
            "fecha_adquisicion": "2025-01-15",
            "cantidad_animales": 50,
            "peso_promedio_entrada": 100.0,
            "precio_compra_kg": 19.0,
            "duracion_estadia_dias": 2
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/v1/lotes", json=lote_data)
            if response.status_code == 201:
                lote_creado = response.json()
                lote_id = lote_creado['id_lote']
                self.created_resources['lotes'].append(lote_id)
                self.log_test("Crear Lote", True, f"ID: {lote_id}")
            else:
                self.log_test("Crear Lote", False, f"Status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Crear Lote", False, f"Error: {str(e)}")
            return False
        
        # 2. Listar lotes
        try:
            response = self.session.get(f"{self.base_url}/api/v1/lotes")
            if response.status_code == 200:
                lotes = response.json()
                self.log_test("Listar Lotes", True, f"Encontrados {len(lotes)} lotes")
            else:
                self.log_test("Listar Lotes", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("Listar Lotes", False, f"Error: {str(e)}")
        
        # 3. Actualizar lote
        try:
            update_data = {
                "cantidad_animales": 60,
                "peso_promedio_entrada": 105.0,
                "precio_compra_kg": 19.5
            }
            response = self.session.patch(f"{self.base_url}/api/v1/lotes/{lote_id}", json=update_data)
            if response.status_code == 200:
                self.log_test("Actualizar Lote", True, f"ID: {lote_id}")
            else:
                self.log_test("Actualizar Lote", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("Actualizar Lote", False, f"Error: {str(e)}")
        
        return True
    
    def test_costos_crud(self) -> bool:
        """Prueba CRUD completo de costos."""
        print("\n💸 PRUEBAS CRUD - COSTOS")
        print("=" * 40)
        
        if not self.created_resources['lotes']:
            self.log_test("CRUD Costos", False, "No hay lotes disponibles para agregar costos")
            return False
        
        lote_id = self.created_resources['lotes'][0]
        
        # Obtener tipos de costo disponibles
        try:
            response = self.session.get(f"{self.base_url}/api/v1/tipos-costo")
            if response.status_code == 200:
                tipos_costo = response.json()
                if not tipos_costo:
                    self.log_test("CRUD Costos", False, "No hay tipos de costo disponibles")
                    return False
                tipo_id = tipos_costo[0]['id_tipo_costo']
            else:
                self.log_test("CRUD Costos", False, "No se pudieron obtener tipos de costo")
                return False
        except Exception as e:
            self.log_test("CRUD Costos", False, f"Error obteniendo tipos: {str(e)}")
            return False
        
        # 1. Crear costo
        costo_data = {
            "id_tipo_costo": tipo_id,
            "monto": 1000.0,
            "fecha_gasto": "2025-01-15",
            "descripcion": "Costo de prueba - Transporte"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/v1/lotes/{lote_id}/costos", json=costo_data)
            if response.status_code == 201:
                costo_creado = response.json()
                costo_id = costo_creado['id_costo']
                self.created_resources['costos'].append(costo_id)
                self.log_test("Crear Costo", True, f"ID: {costo_id}")
            else:
                self.log_test("Crear Costo", False, f"Status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Crear Costo", False, f"Error: {str(e)}")
            return False
        
        # 2. Listar costos del lote
        try:
            response = self.session.get(f"{self.base_url}/api/v1/lotes/{lote_id}/costos")
            if response.status_code == 200:
                costos = response.json()
                self.log_test("Listar Costos", True, f"Encontrados {len(costos)} costos")
            else:
                self.log_test("Listar Costos", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("Listar Costos", False, f"Error: {str(e)}")
        
        # 3. Actualizar costo
        try:
            update_data = {"monto": 1200.0, "descripcion": "Costo actualizado"}
            response = self.session.patch(f"{self.base_url}/api/v1/lotes/{lote_id}/costos/{costo_id}", json=update_data)
            if response.status_code == 200:
                self.log_test("Actualizar Costo", True, f"ID: {costo_id}")
            else:
                self.log_test("Actualizar Costo", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("Actualizar Costo", False, f"Error: {str(e)}")
        
        # 4. Eliminar costo
        try:
            response = self.session.delete(f"{self.base_url}/api/v1/lotes/{lote_id}/costos/{costo_id}")
            if response.status_code == 200:
                self.log_test("Eliminar Costo", True, f"ID: {costo_id}")
                self.created_resources['costos'].remove(costo_id)
            else:
                self.log_test("Eliminar Costo", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("Eliminar Costo", False, f"Error: {str(e)}")
        
        return True
    
    def test_produccion_crud(self) -> bool:
        """Prueba CRUD completo de producción."""
        print("\n📊 PRUEBAS CRUD - PRODUCCIÓN")
        print("=" * 40)
        
        if not self.created_resources['lotes']:
            self.log_test("CRUD Producción", False, "No hay lotes disponibles para producción")
            return False
        
        lote_id = self.created_resources['lotes'][0]
        
        # 1. Crear producción
        produccion_data = {
            "peso_salida_total": 5000.0,
            "mortalidad_unidades": 2
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/v1/lotes/{lote_id}/produccion", json=produccion_data)
            if response.status_code == 201:
                produccion_creada = response.json()
                produccion_id = produccion_creada['id_produccion']
                self.created_resources['produccion'].append(produccion_id)
                self.log_test("Crear Producción", True, f"ID: {produccion_id}")
            else:
                self.log_test("Crear Producción", False, f"Status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Crear Producción", False, f"Error: {str(e)}")
            return False
        
        # 2. Actualizar producción
        try:
            update_data = {"peso_salida_total": 5200.0, "mortalidad_unidades": 1}
            response = self.session.patch(f"{self.base_url}/api/v1/lotes/{lote_id}/produccion", json=update_data)
            if response.status_code == 200:
                self.log_test("Actualizar Producción", True, f"Lote ID: {lote_id}")
            else:
                self.log_test("Actualizar Producción", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("Actualizar Producción", False, f"Error: {str(e)}")
        
        return True
    
    def test_analytics(self) -> bool:
        """Prueba el endpoint de analytics."""
        print("\n📈 PRUEBAS ANALYTICS")
        print("=" * 40)
        
        if not self.created_resources['lotes']:
            self.log_test("Analytics", False, "No hay lotes disponibles para analytics")
            return False
        
        lote_id = self.created_resources['lotes'][0]
        
        try:
            response = self.session.get(f"{self.base_url}/api/v1/lotes/{lote_id}/costos/aggregates")
            if response.status_code == 200:
                analytics = response.json()
                self.log_test("Analytics Costos", True, f"Analytics obtenidos para lote {lote_id}")
                
                # Mostrar datos de analytics
                if 'total_costos' in analytics:
                    print(f"    Total costos: {analytics['total_costos']}")
                if 'costo_fijo_total' in analytics:
                    print(f"    Costo fijo: {analytics['costo_fijo_total']}")
                if 'costo_variable_total' in analytics:
                    print(f"    Costo variable: {analytics['costo_variable_total']}")
            else:
                self.log_test("Analytics Costos", False, f"Status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Analytics Costos", False, f"Error: {str(e)}")
            return False
        
        return True
    
    def test_ml_prediction(self) -> bool:
        """Prueba el endpoint de predicción ML."""
        print("\n🤖 PRUEBAS ML - PREDICCIÓN")
        print("=" * 40)
        
        if not self.created_resources['lotes']:
            self.log_test("Predicción ML", False, "No hay lotes disponibles para predicción")
            return False
        
        lote_id = self.created_resources['lotes'][0]
        
        # 1. Predicción con margen por defecto
        try:
            response = self.session.post(f"{self.base_url}/api/v1/lotes/predict", json={"id_lote": lote_id})
            if response.status_code == 200:
                prediccion = response.json()
                prediccion_id = prediccion.get('prediccion_id')
                if prediccion_id:
                    self.created_resources['predicciones'].append(prediccion_id)
                
                self.log_test("Predicción ML (Margen Defecto)", True, f"Lote ID: {lote_id}")
                print(f"    Precio base: {prediccion.get('precio_base_kg', 'N/A'):.4f} Bs/kg")
                print(f"    Precio sugerido: {prediccion.get('precio_sugerido_kg', 'N/A'):.4f} Bs/kg")
                print(f"    Ganancia neta: {prediccion.get('ganancia_neta_estimada', 'N/A'):.2f} Bs")
                print(f"    Margen aplicado: {prediccion.get('margen_rate', 'N/A')*100:.1f}%")
            else:
                self.log_test("Predicción ML (Margen Defecto)", False, f"Status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Predicción ML (Margen Defecto)", False, f"Error: {str(e)}")
            return False
        
        # 2. Predicción con margen dinámico
        margenes_test = [0.05, 0.10, 0.15, 0.20]
        for margen in margenes_test:
            try:
                response = self.session.post(f"{self.base_url}/api/v1/lotes/predict", 
                                           json={"id_lote": lote_id, "margen_rate": margen})
                if response.status_code == 200:
                    prediccion = response.json()
                    self.log_test(f"Predicción ML (Margen {margen*100:.0f}%)", True, 
                                f"Precio: {prediccion.get('precio_sugerido_kg', 'N/A'):.4f} Bs/kg")
                else:
                    self.log_test(f"Predicción ML (Margen {margen*100:.0f}%)", False, 
                                f"Status {response.status_code}")
            except Exception as e:
                self.log_test(f"Predicción ML (Margen {margen*100:.0f}%)", False, f"Error: {str(e)}")
        
        return True
    
    def test_error_handling(self) -> bool:
        """Prueba el manejo de errores."""
        print("\n⚠️ PRUEBAS MANEJO DE ERRORES")
        print("=" * 40)
        
        # 1. Lote inexistente
        try:
            response = self.session.post(f"{self.base_url}/api/v1/lotes/predict", json={"id_lote": 99999})
            if response.status_code == 500:  # Error esperado
                self.log_test("Error - Lote Inexistente", True, "Error manejado correctamente")
            else:
                self.log_test("Error - Lote Inexistente", False, f"Status inesperado: {response.status_code}")
        except Exception as e:
            self.log_test("Error - Lote Inexistente", False, f"Error: {str(e)}")
        
        # 2. Datos inválidos
        try:
            invalid_data = {"cantidad_animales": -10}  # Valor negativo inválido
            response = self.session.post(f"{self.base_url}/api/v1/lotes", json=invalid_data)
            if response.status_code == 400:  # Error de validación esperado
                self.log_test("Error - Datos Inválidos", True, "Validación funcionando")
            else:
                self.log_test("Error - Datos Inválidos", False, f"Status inesperado: {response.status_code}")
        except Exception as e:
            self.log_test("Error - Datos Inválidos", False, f"Error: {str(e)}")
        
        # 3. Sin autenticación
        try:
            # Crear sesión sin token
            no_auth_session = requests.Session()
            response = no_auth_session.post(f"{self.base_url}/api/v1/lotes", json={"cantidad_animales": 10})
            if response.status_code == 401:  # No autorizado esperado
                self.log_test("Error - Sin Autenticación", True, "Autenticación requerida")
            else:
                self.log_test("Error - Sin Autenticación", False, f"Status inesperado: {response.status_code}")
        except Exception as e:
            self.log_test("Error - Sin Autenticación", False, f"Error: {str(e)}")
        
        return True
    
    def cleanup_resources(self):
        """Limpia los recursos creados durante las pruebas."""
        print("\n🧹 LIMPIEZA DE RECURSOS")
        print("=" * 40)
        
        # Eliminar lotes (esto eliminará costos y producción asociados)
        for lote_id in self.created_resources['lotes']:
            try:
                response = self.session.delete(f"{self.base_url}/api/v1/lotes/{lote_id}")
                if response.status_code == 200:
                    print(f"✅ Lote {lote_id} eliminado")
                else:
                    print(f"❌ Error eliminando lote {lote_id}: {response.status_code}")
            except Exception as e:
                print(f"❌ Error eliminando lote {lote_id}: {str(e)}")
        
        # Eliminar tipos de costo creados
        for tipo_id in self.created_resources['tipos_costo']:
            try:
                response = self.session.delete(f"{self.base_url}/api/v1/tipos-costo/{tipo_id}")
                if response.status_code == 200:
                    print(f"✅ Tipo de costo {tipo_id} eliminado")
                else:
                    print(f"❌ Error eliminando tipo {tipo_id}: {response.status_code}")
            except Exception as e:
                print(f"❌ Error eliminando tipo {tipo_id}: {str(e)}")
    
    def generate_report(self):
        """Genera un reporte completo de las pruebas."""
        print("\n📋 REPORTE DE PRUEBAS")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total de pruebas: {total_tests}")
        print(f"Pruebas exitosas: {passed_tests}")
        print(f"Pruebas fallidas: {failed_tests}")
        print(f"Tasa de éxito: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ PRUEBAS FALLIDAS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['details']}")
        
        # Guardar reporte en archivo
        report_data = {
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': (passed_tests/total_tests)*100,
                'timestamp': datetime.now().isoformat(),
                'base_url': self.base_url
            },
            'test_results': self.test_results,
            'created_resources': self.created_resources
        }
        
        filename = f"api_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Reporte guardado en: {filename}")
        
        return passed_tests == total_tests
    
    def run_complete_test_suite(self) -> bool:
        """Ejecuta la suite completa de pruebas."""
        print("🧪 SUITE DE PRUEBAS UNITARIAS - API BACKEND + ML")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Ejecutar todas las pruebas
        tests = [
            self.test_connection,
            self.authenticate,
            self.test_tipos_costo_crud,
            self.test_lotes_crud,
            self.test_costos_crud,
            self.test_produccion_crud,
            self.test_analytics,
            self.test_ml_prediction,
            self.test_error_handling
        ]
        
        for test in tests:
            try:
                test()
                time.sleep(0.5)  # Pausa entre pruebas
            except Exception as e:
                print(f"❌ Error ejecutando {test.__name__}: {str(e)}")
        
        # Generar reporte
        success = self.generate_report()
        
        # Limpiar recursos
        self.cleanup_resources()
        
        print(f"\n🎯 RESULTADO FINAL: {'✅ TODAS LAS PRUEBAS EXITOSAS' if success else '❌ ALGUNAS PRUEBAS FALLARON'}")
        
        return success

def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Suite de Pruebas Unitarias API Backend + ML')
    parser.add_argument('--url', default='http://127.0.0.1:8000', help='URL del backend')
    parser.add_argument('--no-cleanup', action='store_true', help='No limpiar recursos creados')
    
    args = parser.parse_args()
    
    # Crear suite de pruebas
    test_suite = APITestSuite(args.url)
    
    # Ejecutar pruebas
    success = test_suite.run_complete_test_suite()
    
    # Salir con código apropiado
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
