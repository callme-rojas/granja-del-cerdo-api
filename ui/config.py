"""
Configuración de la aplicación UI
"""
import os

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "https://granja-del-cerdo-api-1.onrender.com")
API_VERSION = "v1"

# Endpoints
LOGIN_ENDPOINT = f"{API_BASE_URL}/api/{API_VERSION}/login"
LOTES_ENDPOINT = f"{API_BASE_URL}/api/{API_VERSION}/lotes"
TIPOS_COSTO_ENDPOINT = f"{API_BASE_URL}/api/{API_VERSION}/tipos-costo"
PREDICT_ENDPOINT = f"{API_BASE_URL}/api/{API_VERSION}/lotes/predict"
DASHBOARD_OVERVIEW_ENDPOINT = f"{API_BASE_URL}/api/{API_VERSION}/dashboard/overview"

# Session State Keys
SESSION_TOKEN = "auth_token"
SESSION_USER = "user"
SESSION_AUTHENTICATED = "authenticated"

# App Configuration
APP_TITLE = "Sistema de Gestión de Reventa de Cerdos"
PAGE_LAYOUT = "wide"

# Mobile Configuration
MOBILE_BREAKPOINT = 768
TOUCH_TARGET_SIZE = 48



