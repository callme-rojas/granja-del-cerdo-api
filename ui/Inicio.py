"""
Sistema de Gestión de Reventa de Cerdos
Aplicación principal
"""
import streamlit as st
import sys
from pathlib import Path

ui_dir = Path(__file__).parent
sys.path.insert(0, str(ui_dir))

from config import APP_TITLE
from utils.auth import is_authenticated, login_page
from utils.styles import inject_custom_css

# Inicializar estado de autenticación
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None
if "auth_token" not in st.session_state:
    st.session_state["auth_token"] = None

# Verificar autenticación usando solo session_state (sin cookies ni localStorage)

if not is_authenticated():
    st.set_page_config(
        page_title="Iniciar Sesión",
        layout="centered",
        initial_sidebar_state="collapsed",
        menu_items=None  # Sin menú
    )
    
    inject_custom_css()
    
    # Ocultar sidebar completamente en login
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        display: none !important;
        visibility: hidden !important;
    }
    button[data-testid="baseButton-header"] {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    login_page()
    st.stop()
else:
    st.set_page_config(
        page_title="Inicio",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    st.switch_page("pages/2_Dashboard.py")
