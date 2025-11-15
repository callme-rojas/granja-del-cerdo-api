"""
Sidebar Simple usando solo componentes nativos de Streamlit
Sin HTML ni JavaScript, diseño minimalista y limpio
"""
import streamlit as st
from typing import Optional, Dict


def render_simple_sidebar(current_page: str = "", user_info: Optional[Dict] = None):
    """
    Renderiza un sidebar simple usando solo componentes nativos de Streamlit.
    
    Args:
        current_page: Nombre de la página actual para marcar como activa
        user_info: Información del usuario actual
    """
    # Ocultar la navegación nativa de Streamlit
    st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
     # CSS mejorado para sidebar
    st.markdown("""
    <style>
    /* Sidebar mejorado */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A0A0A 0%, #1A1A2E 100%) !important;
    }
    
    /* Estilo para botones activos del sidebar */
    .sidebar-active-page {
        background: linear-gradient(135deg, rgba(255, 145, 164, 0.2) 0%, rgba(255, 182, 193, 0.1) 100%) !important;
        border: 2px solid #FF91A4 !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        margin: 0.5rem 0 !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(255, 145, 164, 0.2) !important;
    }
    
    /* Botones de navegación mejorados */
    section[data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: 2px solid #3A3A4A !important;
        color: #E0E0E0 !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        margin: 0.25rem 0 !important;
        transition: all 0.3s ease !important;
        text-align: left !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 145, 164, 0.1) !important;
        border-color: #FF91A4 !important;
        transform: translateX(4px) !important;
        box-shadow: 0 4px 15px rgba(255, 145, 164, 0.15) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        # ========== LOGO Y TÍTULO ==========
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem 0 2rem 0;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem; filter: drop-shadow(0 4px 8px rgba(255, 145, 164, 0.3));">
                🐷
            </div>
            <h1 style="color: #FFFFFF; font-size: 1.5rem; font-weight: 700; margin: 0; letter-spacing: -0.5px;">
                Gestión de Cerdos
            </h1>
            <p style="color: #B0B0B0; font-size: 0.875rem; margin: 0.25rem 0 0 0;">
                Sistema Profesional
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.divider()
        
        # ========== PERFIL DE USUARIO ==========
        if user_info:
            name = user_info.get("name", user_info.get("email", "Usuario"))
            email = user_info.get("email", "")
            
            st.markdown(f"""
            <div style="background: rgba(255, 145, 164, 0.1); border: 1px solid rgba(255, 145, 164, 0.2); border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
                <div style="color: #FFFFFF; font-weight: 600; margin-bottom: 0.25rem;">
                    {name}
                </div>
                <div style="color: #B0B0B0; font-size: 0.875rem;">
                    {email}
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.divider()
        
        # ========== NAVEGACIÓN ==========
        st.markdown("""
        <div style="color: #B0B0B0; font-size: 0.875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.75rem;">
            Navegación
        </div>
        """, unsafe_allow_html=True)
        
        # Definir páginas
        pages = [
            {
                "name": "Dashboard",
                "icon": "📊",
                "page": "pages/2_Dashboard.py",
            },
            {
                "name": "Lotes",
                "icon": "🐷",
                "page": "pages/3_Lotes.py",
            },
            {
                "name": "Costos",
                "icon": "💰",
                "page": "pages/4_Costos.py",
            },
            {
                "name": "Predicciones",
                "icon": "🔮",
                "page": "pages/5_Predicciones.py",
            },
            {
                "name": "Tipos de Costo",
                "icon": "📋",
                "page": "pages/6_Tipos_Costo.py",
            },
        ]
        
        # Renderizar botones de navegación
        for page in pages:
            is_active = current_page in page["page"]
            
            # Si es la página activa, mostrar como texto destacado
            if is_active:
                st.markdown(f"""
                <div class="sidebar-active-page">
                    <span style="font-size: 1.25rem; margin-right: 0.5rem;">{page['icon']}</span>
                    <strong>{page['name']}</strong>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Botón normal con navegación
                if st.button(
                    f"{page['icon']} {page['name']}",
                    key=f"nav_{page['name']}",
                    use_container_width=True,
                ):
                    st.switch_page(page["page"])
        
        st.divider()
        
        # ========== BOTÓN DE CERRAR SESIÓN ==========
        if user_info:
            if st.button("🚪 Cerrar Sesión", key="logout_btn_simple", use_container_width=True):
                from utils.api_client import APIClient
                api = APIClient()
                api.logout()
                st.rerun()
        
        # ========== FOOTER ==========
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; color: #6A6A7A;">
            <div style="font-size: 0.875rem; font-weight: 600; margin-bottom: 0.25rem;">
                Sistema v2.0
            </div>
            <div style="font-size: 0.75rem;">
                © 2024 Gestión de Cerdos
            </div>
        </div>
        """, unsafe_allow_html=True)


def page_config(title: str, icon: str = "📊"):
    """
    Configuración estándar de página
    - Desktop: sidebar siempre visible
    - Móviles: sidebar desplegable/plegable con botón hamburguesa
    
    Args:
        title: Título de la página
        icon: Icono de la página
    """
    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="auto",  # Auto: expandido en desktop, colapsado en móvil
        menu_items=None  # Eliminar menú de configuración
    )

