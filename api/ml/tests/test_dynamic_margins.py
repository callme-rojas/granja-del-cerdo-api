#!/usr/bin/env python3
"""
TEST DE MARGENES DINAMICOS
Prueba el modelo ML con diferentes márgenes dinámicos
"""

import requests
import json
import time
from datetime import datetime

class DynamicMarginTester:
    """Clase para probar márgenes dinámicos en el modelo ML."""
    
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.token = None
        self.results = []
    
    def login(self):
        """Autentica con el backend."""
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
                    print("OK Autenticacion exitosa")
                    return True
            return False
        except Exception as e:
            print(f"ERROR en autenticacion: {e}")
            return False
    
    def create_test_lote(self, scenario_name):
        """Crea un lote de prueba para un escenario específico."""
        # Diferentes tipos de lotes para probar
        lote_templates = {
            "estandar": {
                "fecha_adquisicion": "2025-01-15",
                "cantidad_animales": 50,
                "peso_promedio_entrada": 100.0,
                "precio_compra_kg": 19.0,
                "duracion_estadia_dias": 2
            },
            "pequeno": {
                "fecha_adquisicion": "2025-01-15",
                "cantidad_animales": 25,
                "peso_promedio_entrada": 95.0,
                "precio_compra_kg": 18.5,
                "duracion_estadia_dias": 1
            },
            "grande": {
                "fecha_adquisicion": "2025-01-15",
                "cantidad_animales": 100,
                "peso_promedio_entrada": 105.0,
                "precio_compra_kg": 19.5,
                "duracion_estadia_dias": 3
            },
            "premium": {
                "fecha_adquisicion": "2025-01-15",
                "cantidad_animales": 40,
                "peso_promedio_entrada": 110.0,
                "precio_compra_kg": 22.0,
                "duracion_estadia_dias": 2
            }
        }
        
        lote_data = lote_templates.get(scenario_name, lote_templates["estandar"])
        
        try:
            response = self.session.post(f"{self.base_url}/api/v1/lotes", json=lote_data)
            if response.status_code == 201:
                lote = response.json()
                return lote.get('id_lote')
            return None
        except Exception as e:
            print(f"ERROR creando lote: {e}")
            return None
    
    def add_standard_costs(self, lote_id, lote_data):
        """Agrega costos estándar al lote basado en sus características."""
        tipos_costo = self.get_tipos_costo()
        if not tipos_costo:
            return False
        
        # Calcular costos basados en el lote
        cantidad = lote_data["cantidad_animales"]
        dias = lote_data["duracion_estadia_dias"]
        
        costos_data = [
            {
                "id_tipo_costo": tipos_costo[0]['id_tipo_costo'],
                "monto": cantidad * 20.0,  # Transporte proporcional
                "fecha_gasto": "2025-01-15",
                "descripcion": f"Transporte para {cantidad} animales"
            },
            {
                "id_tipo_costo": tipos_costo[1]['id_tipo_costo'] if len(tipos_costo) > 1 else tipos_costo[0]['id_tipo_costo'],
                "monto": cantidad * dias * 1.5,  # Alimentación por día
                "fecha_gasto": "2025-01-15",
                "descripcion": f"Alimentacion {dias} dias"
            }
        ]
        
        success_count = 0
        for costo in costos_data:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/v1/lotes/{lote_id}/costos",
                    json=costo
                )
                if response.status_code == 201:
                    success_count += 1
            except Exception as e:
                print(f"ERROR agregando costo: {e}")
        
        return success_count > 0
    
    def get_tipos_costo(self):
        """Obtiene los tipos de costo disponibles."""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/tipos-costo")
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"ERROR obteniendo tipos de costo: {e}")
            return []
    
    def make_prediction_with_margin(self, lote_id, margin_rate):
        """Hace una predicción ML con margen específico."""
        try:
            prediction_data = {
                "id_lote": lote_id,
                "margen_rate": margin_rate
            }
            response = self.session.post(
                f"{self.base_url}/api/v1/lotes/predict",
                json=prediction_data
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"ERROR en prediccion: {e}")
            return None
    
    def test_margin_scenario(self, margin_rate, scenario_name, lote_type="estandar"):
        """Prueba un escenario con un margen específico."""
        print(f"\nPROBANDO MARGEN: {margin_rate*100:.1f}% - {scenario_name}")
        print("=" * 60)
        
        # Crear lote de prueba
        lote_data = self.get_lote_template(lote_type)
        lote_id = self.create_test_lote(lote_type)
        if not lote_id:
            print("ERROR creando lote")
            return None
        
        print(f"OK Lote creado: ID {lote_id} ({lote_type})")
        
        # Agregar costos
        if not self.add_standard_costs(lote_id, lote_data):
            print("ERROR agregando costos")
            return None
        
        print("OK Costos agregados")
        
        # Hacer predicción con margen específico
        prediccion = self.make_prediction_with_margin(lote_id, margin_rate)
        if not prediccion:
            print("ERROR en prediccion")
            return None
        
        print("OK Prediccion exitosa")
        
        # Mostrar resultados
        print(f"\nRESULTADOS CON MARGEN {margin_rate*100:.1f}%:")
        print(f"- Precio base: {prediccion.get('precio_base_kg', 'N/A'):.4f} Bs/kg")
        print(f"- Precio sugerido: {prediccion.get('precio_sugerido_kg', 'N/A'):.4f} Bs/kg")
        print(f"- Ganancia neta: {prediccion.get('ganancia_neta_estimada', 'N/A'):.2f} Bs")
        print(f"- Margen aplicado: {prediccion.get('margen_rate', 'N/A')*100:.1f}%")
        
        # Calcular métricas adicionales
        precio_base = prediccion.get('precio_base_kg', 0)
        precio_sugerido = prediccion.get('precio_sugerido_kg', 0)
        ganancia_neta = prediccion.get('ganancia_neta_estimada', 0)
        
        margen_real = ((precio_sugerido - precio_base) / precio_base * 100) if precio_base > 0 else 0
        cantidad_animales = lote_data["cantidad_animales"]
        peso_salida = cantidad_animales * lote_data["peso_promedio_entrada"]
        rentabilidad = (ganancia_neta / (precio_sugerido * peso_salida) * 100) if precio_sugerido > 0 else 0
        
        print(f"- Margen real: {margen_real:.2f}%")
        print(f"- Rentabilidad: {rentabilidad:.2f}%")
        
        # Guardar resultado
        result = {
            "scenario": scenario_name,
            "lote_type": lote_type,
            "margin_rate": margin_rate,
            "lote_id": lote_id,
            "lote_data": lote_data,
            "prediccion": prediccion,
            "margen_real": margen_real,
            "rentabilidad": rentabilidad,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        return result
    
    def get_lote_template(self, lote_type):
        """Obtiene el template de lote para un tipo específico."""
        templates = {
            "estandar": {
                "cantidad_animales": 50,
                "peso_promedio_entrada": 100.0,
                "duracion_estadia_dias": 2
            },
            "pequeno": {
                "cantidad_animales": 25,
                "peso_promedio_entrada": 95.0,
                "duracion_estadia_dias": 1
            },
            "grande": {
                "cantidad_animales": 100,
                "peso_promedio_entrada": 105.0,
                "duracion_estadia_dias": 3
            },
            "premium": {
                "cantidad_animales": 40,
                "peso_promedio_entrada": 110.0,
                "duracion_estadia_dias": 2
            }
        }
        return templates.get(lote_type, templates["estandar"])
    
    def run_comprehensive_margin_tests(self):
        """Ejecuta pruebas exhaustivas de márgenes dinámicos."""
        print("PRUEBAS EXHAUSTIVAS DE MARGENES DINAMICOS")
        print("=" * 60)
        
        if not self.login():
            print("ERROR en autenticacion")
            return False
        
        # Escenarios de prueba
        test_scenarios = [
            # (margin_rate, scenario_name, lote_type)
            (0.05, "Margen Conservador", "estandar"),
            (0.08, "Margen Moderado", "estandar"),
            (0.10, "Margen Estandar", "estandar"),
            (0.12, "Margen Agresivo", "estandar"),
            (0.15, "Margen Alto", "estandar"),
            (0.20, "Margen Premium", "estandar"),
            
            # Pruebas con diferentes tipos de lotes
            (0.10, "Lote Pequeno", "pequeno"),
            (0.10, "Lote Grande", "grande"),
            (0.10, "Lote Premium", "premium"),
            
            # Pruebas extremas
            (0.03, "Margen Minimo", "estandar"),
            (0.25, "Margen Maximo", "estandar"),
        ]
        
        for margin_rate, scenario_name, lote_type in test_scenarios:
            self.test_margin_scenario(margin_rate, scenario_name, lote_type)
            time.sleep(0.5)  # Pausa entre pruebas
        
        # Guardar resultados
        self.save_results()
        
        # Mostrar análisis comparativo
        self.show_comprehensive_analysis()
        
        return True
    
    def save_results(self):
        """Guarda los resultados en un archivo JSON."""
        filename = f"dynamic_margin_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResultados guardados en: {filename}")
    
    def show_comprehensive_analysis(self):
        """Muestra un análisis exhaustivo de los resultados."""
        print(f"\nANALISIS EXHAUSTIVO DE MARGENES DINAMICOS")
        print("=" * 70)
        
        if not self.results:
            print("No hay resultados para mostrar")
            return
        
        print(f"Total de escenarios probados: {len(self.results)}")
        
        # Análisis por margen
        print(f"\nANALISIS POR MARGEN:")
        print(f"{'Margen':<12} {'Escenarios':<12} {'Precio Prom':<12} {'Ganancia Prom':<15} {'Rentabilidad Prom':<18}")
        print("-" * 70)
        
        margin_groups = {}
        for result in self.results:
            margin = result['margin_rate']
            if margin not in margin_groups:
                margin_groups[margin] = []
            margin_groups[margin].append(result)
        
        for margin in sorted(margin_groups.keys()):
            group = margin_groups[margin]
            precio_prom = sum(r['prediccion']['precio_sugerido_kg'] for r in group) / len(group)
            ganancia_prom = sum(r['prediccion']['ganancia_neta_estimada'] for r in group) / len(group)
            rentabilidad_prom = sum(r['rentabilidad'] for r in group) / len(group)
            
            print(f"{margin*100:>5.1f}%{'':<6} {len(group):<12} {precio_prom:<12.2f} {ganancia_prom:<15.0f} {rentabilidad_prom:<18.1f}")
        
        # Análisis por tipo de lote
        print(f"\nANALISIS POR TIPO DE LOTE:")
        print(f"{'Tipo':<12} {'Escenarios':<12} {'Precio Prom':<12} {'Ganancia Prom':<15} {'Rentabilidad Prom':<18}")
        print("-" * 70)
        
        lote_groups = {}
        for result in self.results:
            lote_type = result['lote_type']
            if lote_type not in lote_groups:
                lote_groups[lote_type] = []
            lote_groups[lote_type].append(result)
        
        for lote_type in sorted(lote_groups.keys()):
            group = lote_groups[lote_type]
            precio_prom = sum(r['prediccion']['precio_sugerido_kg'] for r in group) / len(group)
            ganancia_prom = sum(r['prediccion']['ganancia_neta_estimada'] for r in group) / len(group)
            rentabilidad_prom = sum(r['rentabilidad'] for r in group) / len(group)
            
            print(f"{lote_type:<12} {len(group):<12} {precio_prom:<12.2f} {ganancia_prom:<15.0f} {rentabilidad_prom:<18.1f}")
        
        # Recomendaciones finales
        print(f"\nRECOMENDACIONES FINALES:")
        
        # Mejor margen para rentabilidad
        best_rentabilidad = max(self.results, key=lambda x: x['rentabilidad'])
        print(f"- Mejor rentabilidad: {best_rentabilidad['margin_rate']*100:.1f}% ({best_rentabilidad['rentabilidad']:.1f}%)")
        
        # Mejor margen para ganancia absoluta
        best_ganancia = max(self.results, key=lambda x: x['prediccion']['ganancia_neta_estimada'])
        print(f"- Mayor ganancia absoluta: {best_ganancia['margin_rate']*100:.1f}% ({best_ganancia['prediccion']['ganancia_neta_estimada']:.0f} Bs)")
        
        # Margen más balanceado
        balanced_results = [r for r in self.results if 0.08 <= r['margin_rate'] <= 0.15]
        if balanced_results:
            balanced = max(balanced_results, key=lambda x: x['rentabilidad'])
            print(f"- Margen balanceado recomendado: {balanced['margin_rate']*100:.1f}%")

def main():
    """Función principal."""
    tester = DynamicMarginTester()
    success = tester.run_comprehensive_margin_tests()
    
    if success:
        print(f"\nPRUEBAS EXHAUSTIVAS COMPLETADAS")
        print(f"El sistema de margenes dinamicos esta funcionando correctamente")
    else:
        print(f"\nERROR en las pruebas exhaustivas")

if __name__ == "__main__":
    main()
