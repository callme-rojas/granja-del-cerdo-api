"""
Utilidades de autenticación
"""
import streamlit as st
import sys
from pathlib import Path

# Agregar el directorio ui al path
ui_dir = Path(__file__).parent.parent
sys.path.insert(0, str(ui_dir))

from config import SESSION_AUTHENTICATED, SESSION_USER, SESSION_TOKEN
from utils.api_client import APIClient

def is_authenticated() -> bool:
    """Verifica si el usuario está autenticado usando solo session_state"""
    # Usar solo session_state - sin cookies ni localStorage
    return st.session_state.get(SESSION_AUTHENTICATED, False)

def get_current_user():
    """Obtiene el usuario actual"""
    return st.session_state.get(SESSION_USER)

def require_auth():
    """Decorador para requerir autenticación - redirige al login si no está autenticado"""
    # Verificar autenticación usando solo session_state
    if is_authenticated():
        return
    
    # Si no está autenticado, redirigir al login
    _redirect_to_login()

def inject_reload_warning():
    """Función pública para inyectar la advertencia de recarga"""
    if is_authenticated():
        _inject_reload_warning()

def _inject_reload_warning():
    """Inyecta un script que muestra advertencia nativa del navegador antes de recargar"""
    # Inyectar el script usando st.components.v1.html
    import streamlit.components.v1 as components
    
    # Script para mostrar advertencia antes de recargar
    html_code = """
    <script>
    // Configurar advertencia de recarga inmediatamente
    window.addEventListener('load', function() {
        window.addEventListener('beforeunload', function (e) {
            // Cancelar el evento por defecto
            e.preventDefault();
            // Chrome requiere que se establezca returnValue
            e.returnValue = '';
        });
    });
    </script>
    """
    
    # Renderizar el componente HTML
    components.html(html_code, height=0)

def _redirect_to_login():
    """Función auxiliar para redirigir al login"""
    # Intentar usar st.switch_page primero (más confiable)
    try:
        # Intentar redirigir a Inicio.py (archivo principal de login)
        st.switch_page("Inicio.py")
        st.stop()
        return
    except Exception:
        # Si switch_page falla, usar JavaScript
        pass
    
    # Usar JavaScript para redirigir al login
    st.markdown("""
    <script>
    // Redirigir al login eliminando la ruta de la página actual
    (function() {
        const currentUrl = window.location.href;
        let baseUrl = currentUrl;
        
        // Obtener la URL base (sin /pages/...)
        if (currentUrl.includes('/pages/')) {
            baseUrl = currentUrl.split('/pages/')[0];
        } else if (currentUrl.includes('?')) {
            baseUrl = currentUrl.split('?')[0];
        }
        
        // Limpiar la URL base (quitar trailing slash si existe)
        if (baseUrl.endsWith('/')) {
            baseUrl = baseUrl.slice(0, -1);
        }
        
        // Redirigir a la raíz (Inicio.py se carga automáticamente)
        window.location.replace(baseUrl + '/');
    })();
    </script>
    """, unsafe_allow_html=True)
    
    # Mostrar mensaje mientras redirige
    st.warning("🔒 No estás autenticado. Redirigiendo al login...")
    st.stop()

def login_page():
    """Página de inicio de sesión - Diseño minimalista y limpio"""
    
    st.markdown("""
    <style>
    /* Ocultar sidebar y header */
    [data-testid="stSidebar"],
    button[data-testid="baseButton-header"],
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    /* Fondo negro */
    .stApp, .main, .block-container {
        background: #000000 !important;
    }
    
    /* Centrar todo */
    .main .block-container {
        max-width: 400px !important;
        padding: 3rem 1rem !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 100vh !important;
    }
    
    /* Logo */
    .login-logo {
        width: 100px;
        height: 100px;
        background: linear-gradient(135deg, #FF91A4 0%, #FF7F95 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3.5rem;
        margin: 0 auto 2.5rem;
        box-shadow: 0 8px 30px rgba(255, 145, 164, 0.4);
    }
    
    /* Inputs */
    .stTextInput > div > div > input {
        background: #1A1A2E !important;
        border: 1px solid #4A4A5A !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        font-size: 15px !important;
        color: #FFFFFF !important;
        min-height: 50px !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #9A9AAA !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #FF91A4 !important;
        box-shadow: 0 0 0 3px rgba(255, 145, 164, 0.2) !important;
    }
    
    .stTextInput label {
        display: none !important;
    }
    
    /* Ocultar leyendas "press enter to submit" */
    .stTextInput > div[data-testid="InputInstructions"] {
        display: none !important;
    }
    
    /* Botón de mostrar/ocultar contraseña */
    button[data-testid="baseButton-headerNoPadding"] {
        background: #FF91A4 !important;
        color: #FFFFFF !important;
        border-radius: 6px !important;
        padding: 0.25rem 0.5rem !important;
    }
    
    button[data-testid="baseButton-headerNoPadding"]:hover {
        background: #FF7F95 !important;
    }
    
    button[data-testid="baseButton-headerNoPadding"] svg {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }
    
    /* Botón de login */
    .stButton > button,
    .stFormSubmitButton > button {
        width: 100% !important;
        background: #FF91A4 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        min-height: 50px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background: #FF7F95 !important;
    }
    
    /* Mensajes */
    .stAlert {
        background: #1A1A2E !important;
        border: 1px solid #4A4A5A !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
    }
    
    /* Footer */
    .login-footer {
        text-align: center;
        margin-top: 2rem;
        color: #6A6A7A;
        font-size: 0.75rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Logo
    st.markdown('<div class="login-logo">🐷</div>', unsafe_allow_html=True)
    
    api = APIClient()
    
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input(
            "Email",
            placeholder="Email",
            key="login_email",
            label_visibility="collapsed"
        )
        
        password = st.text_input(
            "Contraseña",
            type="password",
            placeholder="Contraseña",
            key="login_password",
            label_visibility="collapsed"
        )
        
        submit = st.form_submit_button("Iniciar Sesión", use_container_width=True)
        
        if submit:
            if not email or not password:
                st.error("Ingresa email y contraseña")
            else:
                with st.spinner("Iniciando sesión..."):
                    result = api.login(email, password)
                    
                    if result["success"]:
                        st.success("Bienvenido")
                        import time
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        status_code = result.get("status_code", 0)
                        if status_code == 401:
                            st.error("Credenciales incorrectas")
                        elif status_code == 0:
                            st.error("Error de conexión")
                        else:
                            st.error("Error al iniciar sesión")
    
    st.markdown('<div class="login-footer">Backend: http://127.0.0.1:8000</div>', unsafe_allow_html=True)

def logout_button():
    """Muestra un botón de cerrar sesión en la barra lateral"""
    if is_authenticated():
        user = get_current_user()
        if user:
            st.sidebar.markdown("---")
            st.sidebar.markdown(f"**Usuario:** {user.get('name', user.get('email', 'Usuario'))}")
            st.sidebar.markdown(f"**Email:** {user.get('email', 'N/A')}")
        
        if st.sidebar.button("Cerrar Sesión", width='stretch'):
            api = APIClient()
            api.logout()
            st.rerun()
