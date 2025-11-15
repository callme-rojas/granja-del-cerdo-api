"""
Cliente API para comunicarse con el backend Flask
"""
import requests
import streamlit as st
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

# Agregar el directorio ui al path
ui_dir = Path(__file__).parent.parent
sys.path.insert(0, str(ui_dir))

from config import (
    LOGIN_ENDPOINT,
    LOTES_ENDPOINT,
    TIPOS_COSTO_ENDPOINT,
    PREDICT_ENDPOINT,
    DASHBOARD_OVERVIEW_ENDPOINT,
    SESSION_TOKEN
)

class APIClient:
    """Cliente para interactuar con la API del backend"""
    
    def __init__(self):
        self.base_url = st.session_state.get("api_base_url", "http://127.0.0.1:8000")
    
    def _get_headers(self) -> Dict[str, str]:
        """Obtiene los headers con el token de autenticación"""
        token = st.session_state.get(SESSION_TOKEN)
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Maneja la respuesta de la API"""
        try:
            if response.status_code in [200, 201]:
                return {"success": True, "data": response.json()}
            else:
                error_data = response.json() if response.content else {}
                return {
                    "success": False,
                    "error": error_data.get("error", "Error desconocido"),
                    "status_code": response.status_code
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al procesar respuesta: {str(e)}",
                "status_code": response.status_code
            }
    
    # Authentication
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Inicia sesión en la API"""
        try:
            response = requests.post(
                LOGIN_ENDPOINT,
                json={"email": email, "password": password},
                headers={"Content-Type": "application/json"}
            )
            result = self._handle_response(response)
            if result["success"]:
                token = result["data"].get("access_token")
                user = result["data"].get("user")
                st.session_state[SESSION_TOKEN] = token
                st.session_state["user"] = user
                st.session_state["authenticated"] = True
            return result
        except Exception as e:
            return {"success": False, "error": f"Error de conexión: {str(e)}"}
    
    def logout(self):
        """Cierra sesión"""
        # Limpiar session_state (sin cookies ni localStorage)
        st.session_state[SESSION_TOKEN] = None
        st.session_state["user"] = None
        st.session_state["authenticated"] = False
    
    # Lotes
    def get_lotes(self) -> Dict[str, Any]:
        """Obtiene todos los lotes"""
        try:
            response = requests.get(LOTES_ENDPOINT, headers=self._get_headers())
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": f"Error de conexión: {str(e)}"}
    
    def get_dashboard_overview(self) -> Dict[str, Any]:
        """Obtiene datos consolidados para el dashboard"""
        try:
            response = requests.get(
                DASHBOARD_OVERVIEW_ENDPOINT,
                headers=self._get_headers(),
                timeout=30
            )
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": f"Error de conexión: {str(e)}"}
    
    def create_lote(self, lote_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo lote"""
        try:
            response = requests.post(
                LOTES_ENDPOINT,
                json=lote_data,
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": f"Error de conexión: {str(e)}"}
    
    def update_lote(self, id_lote: int, lote_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza un lote existente"""
        try:
            response = requests.patch(
                f"{LOTES_ENDPOINT}/{id_lote}",
                json=lote_data,
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": f"Error de conexión: {str(e)}"}
    
    def delete_lote(self, id_lote: int) -> Dict[str, Any]:
        """Elimina un lote"""
        try:
            response = requests.delete(
                f"{LOTES_ENDPOINT}/{id_lote}",
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": f"Error de conexión: {str(e)}"}
    
    # Costos
    def get_costos(self, id_lote: int) -> Dict[str, Any]:
        """Obtiene los costos de un lote"""
        try:
            response = requests.get(
                f"{LOTES_ENDPOINT}/{id_lote}/costos",
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": f"Error de conexión: {str(e)}"}
    
    def create_costo(self, id_lote: int, costo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo costo para un lote"""
        try:
            response = requests.post(
                f"{LOTES_ENDPOINT}/{id_lote}/costos",
                json=costo_data,
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": f"Error de conexión: {str(e)}"}
    
    def update_costo(self, id_lote: int, id_costo: int, costo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza un costo"""
        try:
            response = requests.patch(
                f"{LOTES_ENDPOINT}/{id_lote}/costos/{id_costo}",
                json=costo_data,
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": f"Error de conexión: {str(e)}"}
    
    def delete_costo(self, id_lote: int, id_costo: int) -> Dict[str, Any]:
        """Elimina un costo"""
        try:
            response = requests.delete(
                f"{LOTES_ENDPOINT}/{id_lote}/costos/{id_costo}",
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": f"Error de conexión: {str(e)}"}
    
    # Tipos de Costo
    def get_tipos_costo(self) -> Dict[str, Any]:
        """Obtiene todos los tipos de costo"""
        try:
            response = requests.get(TIPOS_COSTO_ENDPOINT, headers=self._get_headers())
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": f"Error de conexión: {str(e)}"}
    
    def create_tipo_costo(self, tipo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo tipo de costo"""
        try:
            response = requests.post(
                TIPOS_COSTO_ENDPOINT,
                json=tipo_data,
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": f"Error de conexión: {str(e)}"}
    
    # Features
    def get_lote_features(self, id_lote: int, detalle: bool = False) -> Dict[str, Any]:
        """Obtiene las features de un lote"""
        try:
            params = {"detalle": "true" if detalle else "false"}
            response = requests.get(
                f"{LOTES_ENDPOINT}/{id_lote}/features",
                params=params,
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": f"Error de conexión: {str(e)}"}
    
    # Predicción
    def predict_lote(self, id_lote: int, margen_rate: Optional[float] = None) -> Dict[str, Any]:
        """Realiza una predicción de precio para un lote"""
        try:
            data = {"id_lote": id_lote}
            if margen_rate is not None:
                data["margen_rate"] = margen_rate
            
            response = requests.post(
                PREDICT_ENDPOINT,
                json=data,
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": f"Error de conexión: {str(e)}"}

