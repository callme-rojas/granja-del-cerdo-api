"""
Utilidades para páginas Streamlit
Incluye inicialización común de estilos y componentes
"""
import streamlit as st
from utils.styles import inject_custom_css


def init_page(title: str, description: str = ""):
    """
    Inicializa una página con estilos y configuración común
    
    Args:
        title: Título de la página
        description: Descripción opcional de la página
    """
    # Inyectar estilos CSS móvil-first
    inject_custom_css()
    
    # Mostrar título y descripción
    st.title(title)
    if description:
        st.caption(description)
    
    return st


def init_page_with_divider(title: str, description: str = ""):
    """
    Inicializa una página con estilos, título y divisor
    
    Args:
        title: Título de la página
        description: Descripción opcional de la página
    """
    page = init_page(title, description)
    st.markdown("---")
    return page

