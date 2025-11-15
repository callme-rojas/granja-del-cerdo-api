"""
Estilos CSS móvil-first para la aplicación Streamlit
Optimizado para dispositivos móviles (iPhone) y pantallas pequeñas
"""
import streamlit as st

def inject_custom_css():
    """Inyecta estilos CSS personalizados móvil-first"""
    st.markdown("""
    <style>
    /* ===== VARIABLES DE COLOR - TEMA OSCURO CON ROSA PASTEL ===== */
    :root {
        /* Colores principales - Rosa Pastel (tema cerdos) */
        --primary-50: #FFF0F5;
        --primary-100: #FFE4E9;
        --primary-200: #FFD1DC;
        --primary-300: #FFB6C1;
        --primary-400: #FFA5B8;
        --primary-500: #FF91A4;
        --primary-600: #FF7F95;
        --primary-700: #FF6B85;
        --primary-800: #FF5775;
        --primary-900: #FF3D65;
        
        /* Colores semánticos adaptados al tema oscuro */
        --success-color: #A8E6CF;
        --success-light: #2D4A3E;
        --success-dark: #1A2E24;
        
        --warning-color: #FFD3A5;
        --warning-light: #4A3A2A;
        --warning-dark: #2E2419;
        
        --error-color: #FF9AA2;
        --error-light: #4A2A2C;
        --error-dark: #2E191A;
        
        --info-color: #B5EAD7;
        --info-light: #2A4A3E;
        --info-dark: #192E24;
        
        /* Escala de grises oscuros */
        --gray-50: #2D2D3A;
        --gray-100: #3A3A4A;
        --gray-200: #4A4A5A;
        --gray-300: #5A5A6A;
        --gray-400: #6A6A7A;
        --gray-500: #7A7A8A;
        --gray-600: #8A8A9A;
        --gray-700: #9A9AAA;
        --gray-800: #1A1A2E;
        --gray-900: #0F0F1E;
        
        /* Colores de texto (claros para tema oscuro) */
        --text-primary: #FFFFFF;
        --text-secondary: #E0E0E0;
        --text-tertiary: #B0B0B0;
        
        /* Backgrounds negros */
        --bg-primary: #000000;
        --bg-secondary: #0A0A0A;
        --bg-tertiary: #050505;
        
        /* Borders oscuros con toque rosa */
        --border-color: #3A3A4A;
        --border-color-light: #2D2D3A;
        --border-color-dark: #4A4A5A;
        
        /* Sombras profesionales para tema oscuro */
        --shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
        --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.4), 0 1px 2px 0 rgba(0, 0, 0, 0.3);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.5), 0 2px 4px -1px rgba(0, 0, 0, 0.4);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.6), 0 4px 6px -2px rgba(0, 0, 0, 0.5);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.7), 0 10px 10px -5px rgba(0, 0, 0, 0.6);
        --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.8);
        --shadow-pink: 0 4px 20px rgba(255, 145, 164, 0.3);
        
        /* Border radius */
        --radius-sm: 6px;
        --radius: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 20px;
        --radius-full: 9999px;
        
        /* Espaciado */
        --spacing-xs: 0.5rem;
        --spacing-sm: 1rem;
        --spacing-md: 1.5rem;
        --spacing-lg: 2rem;
        --spacing-xl: 3rem;
        --spacing-2xl: 4rem;
        
        /* Transiciones */
        --transition-fast: 150ms;
        --transition-base: 200ms;
        --transition-slow: 300ms;
        --transition-slower: 500ms;
    }
    
    /* ===== RESET Y BASE - TEMA OSCURO ===== */
    * {
        box-sizing: border-box;
    }
    
    /* Fondo oscuro para toda la aplicación */
    .stApp {
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }
    
    /* Ocultar Header de Streamlit completamente */
    header[data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Ocultar botón hamburguesa en desktop, mostrar en móviles */
    @media (min-width: 769px) {
        button[data-testid="baseButton-header"] {
            display: none !important;
            visibility: hidden !important;
        }
    }
    
    /* En móviles, mostrar botón hamburguesa */
    @media (max-width: 768px) {
        button[data-testid="baseButton-header"] {
            display: block !important;
            visibility: visible !important;
            position: fixed !important;
            top: 1rem !important;
            left: 1rem !important;
            z-index: 1001 !important;
            background: var(--bg-secondary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
            padding: 0.5rem !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.8) !important;
            min-width: 44px !important;
            min-height: 44px !important;
            color: var(--text-primary) !important;
        }
        
        button[data-testid="baseButton-header"]:hover {
            background: var(--gray-100) !important;
            border-color: var(--primary-500) !important;
            box-shadow: var(--shadow-pink) !important;
        }
    }
    
    /* Main content area */
    .main {
        padding: 1rem !important;
        background: var(--bg-primary) !important;
    }
    
    /* Block containers */
    .block-container {
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }
    
    /* Sidebar oscuro - fijo en la pantalla */
    section[data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        position: fixed !important;
        height: 100vh !important;
        top: 0 !important;
        left: 0 !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
    }
    
    /* Reducir padding superior del sidebar */
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 0.5rem !important;
    }
    
    /* Scrollbar del sidebar */
    section[data-testid="stSidebar"]::-webkit-scrollbar {
        width: 6px;
    }
    
    section[data-testid="stSidebar"]::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }
    
    section[data-testid="stSidebar"]::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 3px;
    }
    
    section[data-testid="stSidebar"]::-webkit-scrollbar-thumb:hover {
        background: var(--primary-500);
    }
    
    /* En desktop: sidebar siempre visible */
    @media (min-width: 769px) {
        section[data-testid="stSidebar"] {
            position: relative !important;
            transform: translateX(0) !important;
            visibility: visible !important;
            display: block !important;
        }
        
        /* Forzar sidebar siempre expandido en desktop */
        section[data-testid="stSidebar"][aria-expanded="false"] {
            transform: translateX(0) !important;
            visibility: visible !important;
            display: block !important;
        }
    }
    
    /* En móviles: sidebar desplegable con overlay */
    @media (max-width: 768px) {
        section[data-testid="stSidebar"] {
            position: fixed !important;
            z-index: 999 !important;
            height: 100vh !important;
            top: 0 !important;
            left: 0 !important;
            transition: transform 0.3s ease !important;
        }
        
        /* Sidebar cerrado en móviles por defecto */
        section[data-testid="stSidebar"][aria-expanded="false"] {
            transform: translateX(-100%) !important;
        }
        
        /* Sidebar abierto en móviles */
        section[data-testid="stSidebar"][aria-expanded="true"] {
            transform: translateX(0) !important;
            box-shadow: 4px 0 20px rgba(0, 0, 0, 0.8) !important;
        }
        
        /* Overlay oscuro cuando sidebar está abierto */
        section[data-testid="stSidebar"][aria-expanded="true"]::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            z-index: -1;
        }
    }
    
    /* Ocultar sidebar en página de login */
    .stApp[data-testid="stAppViewContainer"]:has([data-testid="stLogin"]) section[data-testid="stSidebar"],
    section[data-testid="stSidebar"]:has([data-testid="stLogin"]) {
        display: none !important;
    }
    
    /* Elementos del sidebar */
    section[data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label {
        color: var(--text-primary) !important;
    }
    
    /* Botones del sidebar */
    section[data-testid="stSidebar"] .stButton > button {
        background: var(--gray-100) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: var(--gray-200) !important;
        border-color: var(--primary-500) !important;
        box-shadow: var(--shadow-pink) !important;
    }
    
    /* Dividers del sidebar */
    section[data-testid="stSidebar"] hr {
        border-color: var(--border-color) !important;
    }
    
    /* Elementos de Streamlit con fondo oscuro */
    .stMarkdown, .stText, .stDataFrame, .stTable {
        color: var(--text-primary) !important;
    }
    
    /* Eliminar cualquier fondo blanco */
    div[data-testid="stAppViewContainer"],
    div[data-testid="stAppViewBlockContainer"] {
        background: var(--bg-primary) !important;
    }
    
    /* ===== TIPOGRAFÍA MÓVIL ===== */
    h1 {
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        line-height: 1.2 !important;
        margin-bottom: 1rem !important;
        color: var(--text-primary) !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        line-height: 1.3 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    h3 {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        line-height: 1.4 !important;
        margin-top: 1rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    p {
        font-size: 1rem !important;
        line-height: 1.6 !important;
        color: var(--text-secondary) !important;
    }
    
    /* ===== BOTONES PROFESIONALES ===== */
    .stButton > button {
        width: 100% !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        border-radius: var(--radius-md) !important;
        border: none !important;
        transition: all var(--transition-base) ease !important;
        box-shadow: var(--shadow-sm) !important;
        min-height: 48px !important;
        cursor: pointer !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    /* Botón primario mejorado */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%) !important;
        color: white !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-lg) !important;
    }
    
    /* Botón secundario - tema oscuro */
    .stButton > button[kind="secondary"] {
        background: var(--gray-100) !important;
        color: var(--text-primary) !important;
        border: 2px solid var(--border-color) !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: var(--gray-200) !important;
        border-color: var(--primary-500) !important;
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-pink) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
        transition: transform 100ms !important;
    }
    
    /* Efecto ripple en botones */
    .stButton > button::after {
        content: '' !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        width: 0 !important;
        height: 0 !important;
        border-radius: 50% !important;
        background: rgba(255, 255, 255, 0.5) !important;
        transform: translate(-50%, -50%) !important;
        transition: width 0.6s, height 0.6s !important;
    }
    
    .stButton > button:active::after {
        width: 300px !important;
        height: 300px !important;
    }
    
    /* ===== INPUTS PROFESIONALES ===== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea,
    .stDateInput > div > div > input {
        font-size: 1rem !important;
        padding: 0.75rem 1rem !important;
        border-radius: var(--radius-md) !important;
        border: 2px solid var(--border-color) !important;
        min-height: 48px !important;
        transition: all var(--transition-base) ease !important;
        background: var(--gray-100) !important;
        color: var(--text-primary) !important;
    }
    
    .stTextInput > div > div > input:hover,
    .stNumberInput > div > div > input:hover,
    .stSelectbox > div > div > select:hover,
    .stTextArea > div > div > textarea:hover,
    .stDateInput > div > div > input:hover {
        border-color: var(--primary-500) !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus,
    .stDateInput > div > div > input:focus {
        border-color: var(--primary-500) !important;
        outline: none !important;
        box-shadow: 0 0 0 4px rgba(255, 145, 164, 0.2) !important;
        background: var(--gray-50) !important;
    }
    
    /* Labels de inputs */
    .stTextInput label,
    .stNumberInput label,
    .stSelectbox label,
    .stTextArea label,
    .stDateInput label {
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* ===== MÉTRICAS Y CARDS PROFESIONALES ===== */
    [data-testid="stMetric"] {
        background: var(--bg-secondary) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1.5rem !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all var(--transition-base) ease !important;
        color: var(--text-primary) !important;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-4px) !important;
        box-shadow: var(--shadow-pink) !important;
        border-color: var(--primary-500) !important;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        line-height: 1.2 !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem !important;
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        margin-bottom: 0.5rem !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.875rem !important;
        font-weight: 600 !important;
    }
    
    /* Expanders profesionales */
    [data-testid="stExpander"] {
        background: var(--bg-primary) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        margin-bottom: 1rem !important;
        overflow: hidden !important;
    }
    
    [data-testid="stExpander"]:hover {
        border-color: var(--primary-300) !important;
    }
    
    /* ===== TABLAS RESPONSIVE ===== */
    .stDataFrame {
        font-size: 0.875rem !important;
        border-radius: var(--radius-small) !important;
        overflow-x: auto !important;
    }
    
    /* ===== SIDEBAR MÓVIL - MEJORADO ===== */
    [data-testid="stSidebar"] {
        background-color: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-color) !important;
        box-shadow: 2px 0 8px rgba(0,0,0,0.8) !important;
        min-width: 250px !important;
        max-width: 300px !important;
        transition: transform 0.3s ease, opacity 0.3s ease !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding: 1rem !important;
        padding-top: 2rem !important;
    }
    
    /* Sidebar content */
    [data-testid="stSidebar"] .element-container {
        margin-bottom: 1rem !important;
    }
    
    /* Sidebar title */
    [data-testid="stSidebar"] h1 {
        font-size: 1.5rem !important;
        margin-bottom: 0.5rem !important;
        color: var(--text-primary) !important;
    }
    
    /* Sidebar caption */
    [data-testid="stSidebar"] .stMarkdown p {
        font-size: 0.875rem !important;
        color: var(--text-secondary) !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Sidebar info boxes */
    [data-testid="stSidebar"] .stAlert {
        padding: 0.75rem !important;
        margin-bottom: 1rem !important;
        border-radius: var(--radius-small) !important;
    }
    
    /* ===== MEJORAR MENÚ DE NAVEGACIÓN DEL SIDEBAR ===== */
    /* Estilos mejorados para el menú de navegación visible */
    [data-testid="stSidebar"] nav[data-testid="stSidebarNav"],
    [data-testid="stSidebar"] section[data-testid="stSidebarNav"] {
        margin-top: 1rem;
    }
    
    [data-testid="stSidebar"] nav[data-testid="stSidebarNav"] ul,
    [data-testid="stSidebar"] section[data-testid="stSidebarNav"] ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    [data-testid="stSidebar"] nav[data-testid="stSidebarNav"] ul li,
    [data-testid="stSidebar"] section[data-testid="stSidebarNav"] ul li {
        margin-bottom: 0.5rem;
    }
    
    [data-testid="stSidebar"] nav[data-testid="stSidebarNav"] ul li a,
    [data-testid="stSidebar"] section[data-testid="stSidebarNav"] ul li a {
        display: block;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        text-decoration: none;
        color: var(--text-primary);
        transition: background-color 0.3s ease;
        font-size: 0.9375rem;
    }
    
    [data-testid="stSidebar"] nav[data-testid="stSidebarNav"] ul li a:hover,
    [data-testid="stSidebar"] section[data-testid="stSidebarNav"] ul li a:hover {
        background-color: var(--bg-secondary);
    }
    
    [data-testid="stSidebar"] nav[data-testid="stSidebarNav"] ul li a[aria-current="page"],
    [data-testid="stSidebar"] section[data-testid="stSidebarNav"] ul li a[aria-current="page"] {
        background-color: var(--primary-color);
        color: white;
        font-weight: 600;
    }
    
    /* ===== TABS PROFESIONALES ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem !important;
        background: var(--bg-secondary) !important;
        padding: 0.5rem !important;
        border-radius: var(--radius-lg) !important;
        margin-bottom: 1.5rem !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem !important;
        font-size: 0.9375rem !important;
        font-weight: 600 !important;
        border-radius: var(--radius-md) !important;
        min-height: 48px !important;
        border: none !important;
        background: transparent !important;
        color: var(--text-secondary) !important;
        transition: all var(--transition-base) ease !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--gray-100) !important;
        color: var(--text-primary) !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: var(--bg-secondary) !important;
        color: var(--primary-500) !important;
        box-shadow: var(--shadow-pink) !important;
        border-bottom: 2px solid var(--primary-500) !important;
    }
    
    /* Panel de contenido de tabs */
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1.5rem !important;
    }
    
    /* ===== ALERTAS Y FEEDBACK PROFESIONALES ===== */
    .stAlert {
        border-radius: var(--radius-md) !important;
        padding: 1.25rem !important;
        margin-bottom: 1rem !important;
        border: 2px solid !important;
        border-left: 4px solid !important;
        box-shadow: var(--shadow-sm) !important;
        font-size: 0.9375rem !important;
        line-height: 1.6 !important;
    }
    
    .stSuccess,
    div[data-baseweb="notification"][kind="success"] {
        background: var(--success-light) !important;
        border-color: var(--success-color) !important;
        border-left-color: var(--success-dark) !important;
        color: var(--success-dark) !important;
    }
    
    .stError,
    div[data-baseweb="notification"][kind="error"] {
        background: var(--error-light) !important;
        border-color: var(--error-color) !important;
        border-left-color: var(--error-dark) !important;
        color: var(--error-dark) !important;
    }
    
    .stWarning,
    div[data-baseweb="notification"][kind="warning"] {
        background: var(--warning-light) !important;
        border-color: var(--warning-color) !important;
        border-left-color: var(--warning-dark) !important;
        color: var(--warning-dark) !important;
    }
    
    .stInfo,
    div[data-baseweb="notification"][kind="info"] {
        background: var(--info-light) !important;
        border-color: var(--info-color) !important;
        border-left-color: var(--info-dark) !important;
        color: var(--info-dark) !important;
    }
    
    /* ===== SPINNER Y LOADING ===== */
    .stSpinner > div {
        border-color: var(--primary-color) transparent transparent transparent !important;
    }
    
    /* ===== FORMULARIOS MÓVILES ===== */
    .stForm {
        border: 2px solid var(--border-color) !important;
        border-radius: var(--radius) !important;
        padding: 1.5rem !important;
        background-color: var(--bg-primary) !important;
        box-shadow: var(--shadow) !important;
        margin-bottom: 1.5rem !important;
    }
    
    /* ===== CONTAINERS Y COLUMNAS ===== */
    .stContainer {
        padding: 1rem !important;
    }
    
    /* ===== CONTENIDO PRINCIPAL RESPONSIVE ===== */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }
    
    /* En móviles, las columnas se apilan verticalmente */
    @media (max-width: 768px) {
        /* Contenedor principal */
        .main {
            padding: 0.5rem !important;
            width: 100% !important;
        }
        
        .main .block-container {
            padding: 1rem 0.75rem !important;
            max-width: 100% !important;
        }
        
        /* Columnas se apilan */
        .element-container {
            width: 100% !important;
            margin-bottom: 1rem !important;
        }
        
        [data-testid="column"] {
            width: 100% !important;
            min-width: 100% !important;
            flex: 1 1 100% !important;
            margin-bottom: 1rem !important;
        }
        
        /* Sidebar mejorado en móviles */
        [data-testid="stSidebar"] {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            height: 100vh !important;
            z-index: 999 !important;
            transform: translateX(-100%) !important;
            transition: transform 0.3s ease !important;
        }
        
        /* Sidebar cuando está abierto */
        [data-testid="stSidebar"][aria-expanded="true"] {
            transform: translateX(0) !important;
        }
        
        /* Overlay cuando sidebar está abierto */
        .main::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 998;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }
        
        /* Ajustar contenido cuando sidebar está abierto */
        [data-testid="stSidebar"][aria-expanded="true"] ~ .main::before {
            opacity: 1;
            pointer-events: all;
        }
        
        /* Botón hamburguesa visible en móviles (ya definido arriba) */
        
        /* Tamaños de fuente más pequeños en móviles */
        h1 {
            font-size: 1.5rem !important;
            line-height: 1.3 !important;
        }
        
        h2 {
            font-size: 1.25rem !important;
            line-height: 1.4 !important;
        }
        
        h3 {
            font-size: 1.125rem !important;
            line-height: 1.5 !important;
        }
        
        /* Información boxes más compactas */
        .stAlert {
            padding: 0.75rem !important;
            font-size: 0.875rem !important;
        }
        
        /* Botones full width en móviles */
        .stButton > button {
            width: 100% !important;
            min-height: 44px !important;
        }
        
        /* Inputs más grandes en móviles */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select {
            min-height: 44px !important;
            font-size: 16px !important; /* Previene zoom en iOS */
        }
        
        /* Tablas scroll horizontal */
        .stDataFrame {
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
        }
    }
    
    /* ===== MEJORAS PARA IPHONE Y DISPOSITIVOS PEQUEÑOS ===== */
    @media (max-width: 414px) {
        /* iPhone y dispositivos pequeños */
        .main {
            padding: 0.5rem !important;
        }
        
        .main .block-container {
            padding: 0.75rem 0.5rem !important;
        }
        
        h1 {
            font-size: 1.375rem !important;
            margin-bottom: 0.75rem !important;
            line-height: 1.3 !important;
        }
        
        h2 {
            font-size: 1.125rem !important;
        }
        
        h3 {
            font-size: 1rem !important;
        }
        
        .stButton > button {
            font-size: 0.9375rem !important;
            padding: 0.75rem 1rem !important;
            min-height: 44px !important;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1.25rem !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.8125rem !important;
        }
        
        /* Sidebar más compacto en iPhone */
        [data-testid="stSidebar"] {
            min-width: 240px !important;
            max-width: 280px !important;
        }
        
        [data-testid="stSidebar"] h1 {
            font-size: 1.25rem !important;
        }
        
        /* Tabs más compactas */
        .stTabs [data-baseweb="tab"] {
            padding: 0.5rem 0.75rem !important;
            font-size: 0.8125rem !important;
        }
        
        /* Inputs prevenir zoom en iOS */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > div > textarea {
            font-size: 16px !important;
            min-height: 44px !important;
        }
    }
    
    /* ===== MEJORAS ESPECÍFICAS PARA MÓVILES ===== */
    @media (max-width: 480px) {
        /* Pantallas muy pequeñas */
        .main .block-container {
            padding: 0.5rem !important;
        }
        
        /* Columnas siempre en una sola fila */
        [data-testid="column"] {
            flex-basis: 100% !important;
            max-width: 100% !important;
        }
        
        /* Espaciado reducido */
        .element-container {
            margin-bottom: 0.75rem !important;
        }
    }
    
    /* ===== UTILIDADES ===== */
    .mobile-hidden {
        display: none !important;
    }
    
    @media (min-width: 769px) {
        .mobile-hidden {
            display: block !important;
        }
        
        .desktop-hidden {
            display: none !important;
        }
    }
    
    /* ===== ANIMACIONES ===== */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in {
        animation: fadeIn 0.3s ease-in-out;
    }
    
    /* ===== MEJORAS DE ACCESIBILIDAD ===== */
    button:focus,
    input:focus,
    select:focus,
    textarea:focus {
        outline: 2px solid var(--primary-color) !important;
        outline-offset: 2px !important;
    }
    
    /* ===== SCROLLBAR PERSONALIZADA ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-secondary);
    }
    
    /* ===== MEJORAS DE RENDIMIENTO ===== */
    img, iframe {
        max-width: 100%;
        height: auto;
    }
    
    /* ===== ESTADOS DE CARGA ===== */
    .loading-state {
        opacity: 0.6;
        pointer-events: none;
    }
    
    /* ===== TOOLTIPS ===== */
    [data-testid="stTooltip"] {
        font-size: 0.875rem !important;
    }
    
    /* Botón hamburguesa solo visible en móviles (definido arriba en media queries) */
    
    /* ===== SIDEBAR OVERLAY EN MÓVILES ===== */
    @media (max-width: 768px) {
        /* Overlay cuando sidebar está abierto */
        [data-testid="stSidebar"][aria-expanded="true"] {
            box-shadow: 2px 0 12px rgba(0,0,0,0.15) !important;
        }
        
        /* Prevenir scroll del body cuando sidebar está abierto */
        body:has([data-testid="stSidebar"][aria-expanded="true"]) {
            overflow: hidden !important;
        }
    }
    
    /* ===== MEJORAS DE RESPONSIVIDAD EN MÓVILES ===== */
    @media (max-width: 768px) {
        /* Asegurar que el contenido principal use todo el ancho */
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }
        
        /* Columnas siempre full width en móviles */
        [data-testid="column"] {
            width: 100% !important;
            min-width: 0 !important;
            flex: 0 0 100% !important;
        }
        
        /* Tabs más compactas en móviles */
        .stTabs [data-baseweb="tab-list"] {
            flex-wrap: wrap !important;
            gap: 0.25rem !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            flex: 1 1 auto !important;
            min-width: calc(50% - 0.125rem) !important;
            font-size: 0.8125rem !important;
            padding: 0.5rem 0.75rem !important;
        }
        
        /* Formularios más compactos */
        .stForm {
            padding: 1rem !important;
        }
        
        /* Métricas más compactas */
        [data-testid="stMetricValue"] {
            font-size: 1.375rem !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.8125rem !important;
        }
    }
    
    /* ===== MEJORAS ESPECÍFICAS PARA IPHONE ===== */
    @media (max-width: 414px) {
        /* Sidebar más estrecho en iPhone */
        [data-testid="stSidebar"] {
            width: 280px !important;
            max-width: 85vw !important;
        }
        
        /* Sidebar siempre visible en móviles también */
        [data-testid="stSidebar"] {
            transform: translateX(0) !important;
            position: relative !important;
        }
        
        /* Contenido principal más compacto */
        .main .block-container {
            padding: 0.5rem !important;
        }
        
        /* Tabs en una sola fila */
        .stTabs [data-baseweb="tab"] {
            min-width: calc(33.333% - 0.167rem) !important;
            font-size: 0.75rem !important;
            padding: 0.5rem !important;
        }
    }
    
    /* ===== MEJORAS DE TOUCH EN MÓVILES ===== */
    @media (hover: none) and (pointer: coarse) {
        /* Dispositivos táctiles */
        button, a, [role="button"] {
            min-height: 44px !important;
            min-width: 44px !important;
        }
        
        /* Áreas táctiles más grandes */
        .stButton > button {
            padding: 0.875rem 1.25rem !important;
        }
        
        /* Inputs más grandes para evitar zoom en iOS */
        input[type="text"],
        input[type="number"],
        input[type="email"],
        input[type="password"],
        select,
        textarea {
            font-size: 16px !important;
            min-height: 44px !important;
        }
    }
    
    /* ===== PREVENIR ZOOM EN IOS ===== */
    @supports (-webkit-touch-callout: none) {
        /* iOS específico */
        input[type="text"],
        input[type="number"],
        input[type="email"],
        input[type="password"],
        select,
        textarea {
            font-size: 16px !important;
        }
    }
    </style>
    
    <script>
    // Mejorar comportamiento del sidebar en móviles
    document.addEventListener('DOMContentLoaded', function() {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        const hamburgerButton = document.querySelector('button[data-testid="baseButton-header"]');
        
        // Función para actualizar según el tamaño de pantalla
        function updateSidebarBehavior() {
            if (window.innerWidth > 768) {
                // Desktop: ocultar botón y forzar sidebar visible
                if (hamburgerButton) {
                    hamburgerButton.style.display = 'none';
                }
                
                if (sidebar) {
                    sidebar.setAttribute('aria-expanded', 'true');
                    sidebar.style.transform = 'translateX(0)';
                }
            } else {
                // Móviles: mostrar botón y permitir toggle
                if (hamburgerButton) {
                    hamburgerButton.style.display = 'block';
                }
            }
        }
        
        // Ejecutar al cargar
        updateSidebarBehavior();
        
        // Ejecutar al cambiar tamaño de ventana
        window.addEventListener('resize', updateSidebarBehavior)
        
        if (sidebar && hamburgerButton) {
            // Cerrar sidebar al hacer clic fuera en móviles
            document.addEventListener('click', function(event) {
                if (window.innerWidth <= 768) {
                    const isClickInsideSidebar = sidebar.contains(event.target);
                    const isClickOnHamburger = hamburgerButton.contains(event.target);
                    
                    if (!isClickInsideSidebar && !isClickOnHamburger && sidebar.getAttribute('aria-expanded') === 'true') {
                        // El sidebar se cerrará automáticamente por Streamlit
                    }
                }
            });
            
            // Prevenir scroll del body cuando sidebar está abierto
            const sidebarObserver = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.type === 'attributes' && mutation.attributeName === 'aria-expanded') {
                        if (sidebar.getAttribute('aria-expanded') === 'true') {
                            document.body.style.overflow = 'hidden';
                        } else {
                            document.body.style.overflow = '';
                        }
                    }
                });
            });
            
            sidebarObserver.observe(sidebar, {
                attributes: true,
                attributeFilter: ['aria-expanded']
            });
        }
    });
    </script>
    """, unsafe_allow_html=True)


def get_mobile_css():
    """Retorna CSS adicional para móviles"""
    return """
    <style>
    /* CSS adicional para optimización móvil */
    @media (max-width: 768px) {
        /* Espaciado reducido en móviles */
        .element-container {
            margin-bottom: 0.75rem !important;
        }
        
        /* Botones más grandes en móviles */
        .stButton > button {
            min-height: 52px !important;
            font-size: 1.0625rem !important;
        }
        
        /* Inputs más grandes */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select {
            min-height: 52px !important;
            font-size: 1.0625rem !important;
        }
    }
    </style>
    """

