"""
Estilos CSS mejorados adicionales para efectos modernos
"""
import streamlit as st

def inject_enhanced_styles():
    """Inyecta estilos CSS mejorados con efectos modernos"""
    st.markdown("""
    <style>
    /* ===== INPUTS CON EFECTOS GLASSMORPHISM ===== */
    .stTextInput > div > div,
    .stNumberInput > div > div,
    .stSelectbox > div > div,
    .stTextArea > div > div,
    .stDateInput > div > div {
        position: relative;
    }
    
    /* Efecto de brillo en hover para inputs */
    .stTextInput > div > div > input:hover,
    .stNumberInput > div > div > input:hover,
    .stSelectbox > div > div > select:hover,
    .stTextArea > div > div > textarea:hover {
        background: linear-gradient(135deg, var(--gray-100) 0%, var(--gray-50) 100%) !important;
        box-shadow: 0 0 20px rgba(255, 145, 164, 0.1) !important;
    }
    
    /* Animación de enfoque mejorada */
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus {
        background: var(--gray-50) !important;
        border-color: var(--primary-500) !important;
        box-shadow: 
            0 0 0 4px rgba(255, 145, 164, 0.15),
            0 8px 24px rgba(255, 145, 164, 0.2),
            inset 0 1px 3px rgba(255, 255, 255, 0.05) !important;
        transform: translateY(-1px) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    /* ===== BOTONES CON GRADIENTES ANIMADOS ===== */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 50%, var(--primary-700) 100%) !important;
        background-size: 200% 200% !important;
        animation: gradientShift 3s ease infinite !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Brillo en hover */
    .stButton > button[kind="primary"]:hover {
        box-shadow: 
            0 0 30px rgba(255, 145, 164, 0.4),
            0 10px 25px rgba(255, 145, 164, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
    }
    
    /* ===== SLIDERS MEJORADOS ===== */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, var(--primary-400), var(--primary-600)) !important;
    }
    
    .stSlider > div > div > div > div > div {
        background: white !important;
        border: 3px solid var(--primary-500) !important;
        box-shadow: 0 0 15px rgba(255, 145, 164, 0.5) !important;
        width: 24px !important;
        height: 24px !important;
    }
    
    .stSlider > div > div > div > div > div:hover {
        transform: scale(1.2) !important;
        box-shadow: 0 0 25px rgba(255, 145, 164, 0.8) !important;
    }
    
    /* ===== CHECKBOXES Y RADIOS MEJORADOS ===== */
    .stCheckbox > label > div,
    .stRadio > label > div {
        border-radius: 6px !important;
        transition: all 0.3s ease !important;
    }
    
    .stCheckbox > label:hover,
    .stRadio > label:hover {
        background: var(--gray-100) !important;
        border-radius: 8px !important;
        padding: 0.25rem !important;
    }
    
    /* ===== SELECTBOX CON DROPDOWN MEJORADO ===== */
    .stSelectbox > div > div > div[role="listbox"] {
        background: var(--bg-secondary) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stSelectbox > div > div > div[role="option"]:hover {
        background: linear-gradient(90deg, var(--primary-500) 0%, var(--primary-600) 100%) !important;
        color: white !important;
    }
    
    /* ===== FORMULARIOS CON GLASSMORPHISM ===== */
    .stForm {
        background: linear-gradient(135deg, rgba(42, 42, 58, 0.8) 0%, rgba(26, 26, 46, 0.9) 100%) !important;
        backdrop-filter: blur(20px) !important;
        border: 2px solid rgba(255, 145, 164, 0.2) !important;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.6),
            inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
    }
    
    .stForm:hover {
        border-color: rgba(255, 145, 164, 0.4) !important;
        box-shadow: 
            0 12px 40px rgba(0, 0, 0, 0.7),
            0 0 30px rgba(255, 145, 164, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
    }
    
    /* ===== DATAFRAMES CON ESTILO MODERNO ===== */
    .stDataFrame {
        border-radius: var(--radius-lg) !important;
        overflow: hidden !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5) !important;
    }
    
    .stDataFrame table {
        border-collapse: separate !important;
        border-spacing: 0 !important;
    }
    
    .stDataFrame thead th {
        background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 1rem !important;
        border: none !important;
    }
    
    .stDataFrame tbody tr:nth-child(even) {
        background: var(--gray-100) !important;
    }
    
    .stDataFrame tbody tr:hover {
        background: var(--gray-50) !important;
        transform: scale(1.01) !important;
        box-shadow: 0 4px 12px rgba(255, 145, 164, 0.2) !important;
    }
    
    .stDataFrame tbody td {
        padding: 0.875rem !important;
        border-bottom: 1px solid var(--border-color) !important;
    }
    
    /* ===== FILE UPLOADER MEJORADO ===== */
    .stFileUploader > div > div {
        border: 3px dashed var(--border-color) !important;
        border-radius: var(--radius-lg) !important;
        background: linear-gradient(135deg, var(--gray-100) 0%, var(--gray-50) 100%) !important;
        padding: 2rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader > div > div:hover {
        border-color: var(--primary-500) !important;
        background: linear-gradient(135deg, var(--gray-50) 0%, var(--gray-100) 100%) !important;
        box-shadow: 0 0 30px rgba(255, 145, 164, 0.2) !important;
        transform: translateY(-2px) !important;
    }
    
    /* ===== PROGRESS BAR MEJORADO ===== */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--primary-400), var(--primary-600), var(--primary-500)) !important;
        background-size: 200% 100% !important;
        animation: progressShine 2s ease infinite !important;
        border-radius: 10px !important;
        box-shadow: 0 0 20px rgba(255, 145, 164, 0.5) !important;
    }
    
    @keyframes progressShine {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* ===== TOOLTIPS MEJORADOS ===== */
    [data-testid="stTooltipIcon"] {
        color: var(--primary-500) !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stTooltipIcon"]:hover {
        color: var(--primary-400) !important;
        transform: scale(1.2) rotate(15deg) !important;
    }
    
    /* ===== DIVIDERS ESTILIZADOS ===== */
    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, var(--primary-500), transparent) !important;
        margin: 2rem 0 !important;
        opacity: 0.5 !important;
    }
    
    /* ===== ANIMACIONES DE ENTRADA ===== */
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes scaleIn {
        from {
            opacity: 0;
            transform: scale(0.9);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    /* Aplicar animaciones a elementos */
    .element-container {
        animation: slideInUp 0.4s ease-out !important;
    }
    
    [data-testid="stMetric"] {
        animation: scaleIn 0.5s ease-out !important;
    }
    
    .stButton > button {
        animation: slideInUp 0.3s ease-out !important;
    }
    
    /* ===== EFECTOS DE PULSO EN BOTONES ===== */
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.05); opacity: 0.8; }
    }
    
    /* ===== MEJORAS DE ACCESIBILIDAD CON ESTILO ===== */
    *:focus-visible {
        outline: 3px solid var(--primary-500) !important;
        outline-offset: 3px !important;
        border-radius: 4px !important;
    }
    
    /* ===== RESPONSIVE ENHANCEMENTS ===== */
    @media (max-width: 768px) {
        /* Inputs más grandes en móviles */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select {
            padding: 1rem !important;
            font-size: 16px !important;
        }
        
        /* Botones más prominentes */
        .stButton > button {
            padding: 1rem 1.5rem !important;
            font-size: 1.125rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
