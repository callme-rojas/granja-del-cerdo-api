"""
Gestión de Tipos de Costo - Versión Profesional
Catálogo de tipos de costo con análisis de uso
"""
import streamlit as st
import sys
from pathlib import Path
import pandas as pd

ui_dir = Path(__file__).parent.parent
sys.path.insert(0, str(ui_dir))

from utils.auth import require_auth, get_current_user, inject_reload_warning
from utils.api_client import APIClient
from utils.advanced_charts import (
    animated_bar_chart, interactive_donut_chart,
    display_chart, CORPORATE_COLORS
)
from utils.professional_components import (
    metric_card, modern_card, alert_modern, empty_state_modern,
    badge, stats_card_row
)
from utils.simple_sidebar import page_config, render_simple_sidebar
from utils.styles import inject_custom_css

# Configuración
page_config("Tipos de Costo", "📋")

require_auth()
inject_custom_css()
inject_reload_warning()

# Sidebar simple
user = get_current_user()
render_simple_sidebar("6_Tipos_Costo.py", user)

# CSS profesional con tema oscuro
st.markdown("""
<style>
    .catalog-header {
        background: linear-gradient(135deg, rgba(255, 145, 164, 0.15) 0%, rgba(255, 127, 149, 0.15) 100%);
        border: 1px solid rgba(255, 145, 164, 0.3);
        color: #FFFFFF;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 30px rgba(255, 145, 164, 0.2);
        backdrop-filter: blur(10px);
    }
    .catalog-header h1 {
        background: linear-gradient(135deg, #FF91A4 0%, #FF7F95 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 0.5rem 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(255, 145, 164, 0.4);
    }
    .category-badge-fijo {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(37, 99, 235, 0.2) 100%);
        border: 1px solid rgba(59, 130, 246, 0.5);
        color: #60A5FA;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin: 0.25rem;
    }
    .category-badge-variable {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(217, 119, 6, 0.2) 100%);
        border: 1px solid rgba(245, 158, 11, 0.5);
        color: #FBBF24;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# API Client
api = APIClient()

# ========== HEADER ==========
st.markdown("""
<div class="catalog-header">
    <h1 style="margin: 0 0 0.5rem 0; font-size: 2.5rem;">Catálogo de Tipos de Costo</h1>
    <p style="margin: 0; font-size: 1.125rem; opacity: 0.95;">Gestiona y organiza los tipos de costo de tu sistema</p>
</div>
""", unsafe_allow_html=True)

# ========== TABS ==========

tab1, tab2 = st.tabs(["📊 Catálogo y Análisis", "➕ Crear Tipo de Costo"])

# ========== TAB 1: CATÁLOGO ==========

with tab1:
    st.markdown('<div class="section-title">Tipos de Costo Registrados</div>', unsafe_allow_html=True)
    
    col_refresh = st.columns([3, 1])
    with col_refresh[1]:
        if st.button("⟳ Actualizar", use_container_width=True):
            st.rerun()
    
    with st.spinner("Cargando tipos de costo..."):
        result = api.get_tipos_costo()
        
        if result["success"]:
            tipos = result["data"]
            
            if tipos:
                df_tipos = pd.DataFrame(tipos)
                
                # KPIs
                total_tipos = len(tipos)
                tipos_fijos = len([t for t in tipos if t.get("categoria") == "FIJO"])
                tipos_variables = len([t for t in tipos if t.get("categoria") == "VARIABLE"])
                
                stats = [
                    {
                        "label": "Total Tipos",
                        "value": f"{total_tipos}",
                        "icon": "📋",
                        "color": "info"
                    },
                    {
                        "label": "Costos Fijos",
                        "value": f"{tipos_fijos}",
                        "icon": "📊",
                        "color": "primary"
                    },
                    {
                        "label": "Costos Variables",
                        "value": f"{tipos_variables}",
                        "icon": "📈",
                        "color": "warning"
                    },
                    {
                        "label": "Más Común",
                        "value": "FIJO" if tipos_fijos > tipos_variables else "VARIABLE",
                        "icon": "⭐",
                        "color": "success"
                    }
                ]
                
                stats_card_row(stats)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Filtros
                col_f1, col_f2 = st.columns(2)
                
                with col_f1:
                    categoria_filter = st.selectbox("Filtrar por categoría", ["Todas", "FIJO", "VARIABLE"])
                
                with col_f2:
                    search_term = st.text_input("Buscar por nombre", placeholder="Buscar...")
                
                # Aplicar filtros
                filtered_tipos = tipos
                if categoria_filter != "Todas":
                    filtered_tipos = [t for t in filtered_tipos if t.get("categoria") == categoria_filter]
                if search_term:
                    filtered_tipos = [t for t in filtered_tipos if search_term.lower() in t.get("nombre_tipo", "").lower()]
                
                st.markdown(f"**Mostrando {len(filtered_tipos)} de {total_tipos} tipos**")
                
                # Gráficos
                col_g1, col_g2 = st.columns(2)
                
                with col_g1:
                    # Donut de distribución
                    fig1 = interactive_donut_chart(
                        labels=['Fijos', 'Variables'],
                        values=[tipos_fijos, tipos_variables],
                        title="Distribución por Categoría",
                        colors=[CORPORATE_COLORS["primary"], CORPORATE_COLORS["warning"]]
                    )
                    display_chart(fig1, key="tipos_donut")
                
                with col_g2:
                    # Barras por categoría
                    df_categoria = pd.DataFrame({
                        'Categoría': ['FIJO', 'VARIABLE'],
                        'Cantidad': [tipos_fijos, tipos_variables]
                    })
                    
                    fig2 = animated_bar_chart(
                        data=df_categoria,
                        x_col='Categoría',
                        y_col='Cantidad',
                        title="Cantidad por Categoría",
                        show_values=True
                    )
                    display_chart(fig2, key="tipos_bar")
                
                # Tabla mejorada
                st.markdown('<div class="section-title">Detalle del Catálogo</div>', unsafe_allow_html=True)
                
                if filtered_tipos:
                    # Crear tabla con badges (tema oscuro)
                    st.markdown("""
                    <div style="background: rgba(26, 26, 46, 0.6); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255, 145, 164, 0.2);">
                    """, unsafe_allow_html=True)
                    
                    for tipo in filtered_tipos:
                        categoria_class = "category-badge-fijo" if tipo.get("categoria") == "FIJO" else "category-badge-variable"
                        
                        st.markdown(f"""
                        <div style="
                            padding: 1rem;
                            margin-bottom: 0.75rem;
                            border: 1px solid rgba(255, 145, 164, 0.2);
                            border-radius: 10px;
                            background: rgba(26, 26, 46, 0.4);
                            transition: all 0.3s ease;
                        " onmouseover="this.style.borderColor='rgba(255, 145, 164, 0.5)'; this.style.background='rgba(26, 26, 46, 0.7)';"
                           onmouseout="this.style.borderColor='rgba(255, 145, 164, 0.2)'; this.style.background='rgba(26, 26, 46, 0.4)';">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="font-weight: 600; font-size: 1.125rem; color: #FFFFFF; margin-bottom: 0.25rem;">
                                        {tipo.get('nombre_tipo', 'Sin nombre')}
                                    </div>
                                    <div style="font-size: 0.875rem; color: #9A9AAA;">
                                        Número: {tipo.get('id_tipo_costo', 'N/A')}
                                    </div>
                                </div>
                                <div class="{categoria_class}">
                                    {tipo.get('categoria', 'N/A')}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.info("No se encontraron tipos con los filtros aplicados")
                
                # Información de categorías
                st.markdown('<div class="section-title">Guía de Categorías</div>', unsafe_allow_html=True)
                
                col_info1, col_info2 = st.columns(2)
                
                with col_info1:
                    st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%);
                        padding: 1.5rem;
                        border-radius: 12px;
                        border: 1px solid rgba(59, 130, 246, 0.3);
                    ">
                        <h3 style="color: #60A5FA; margin-top: 0;">Costos FIJOS</h3>
                        <ul style="color: #E5E7EB; line-height: 1.8;">
                            <li><strong>Definición:</strong> No varían con la cantidad</li>
                            <li><strong>Ejemplos:</strong> Alquiler, servicios, mantenimiento</li>
                            <li><strong>Cálculo:</strong> Se distribuyen entre todos los kg</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_info2:
                    st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.1) 100%);
                        padding: 1.5rem;
                        border-radius: 12px;
                        border: 1px solid rgba(245, 158, 11, 0.3);
                    ">
                        <h3 style="color: #FBBF24; margin-top: 0;">Costos VARIABLES</h3>
                        <ul style="color: #E5E7EB; line-height: 1.8;">
                            <li><strong>Definición:</strong> Varían con la cantidad</li>
                            <li><strong>Ejemplos:</strong> Alimentación, transporte</li>
                            <li><strong>Cálculo:</strong> Por animal o por kg</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                
            else:
                empty_state_modern(
                    icon="📋",
                    title="No hay tipos de costo registrados",
                    description="Crea tu primer tipo de costo para comenzar a categorizar gastos."
                )
        else:
            alert_modern(f"Error: {result.get('error', 'Error desconocido')}", "error")

# ========== TAB 2: CREAR ==========

with tab2:
    st.markdown('<div class="section-title">Crear Nuevo Tipo de Costo</div>', unsafe_allow_html=True)
    
    with st.form("create_tipo_form", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 📝 Información del Tipo")
            
            nombre_tipo = st.text_input(
                "Nombre del Tipo *",
                placeholder="Ej: Alimentación, Logística, Mantenimiento...",
                help="Mínimo 3 caracteres"
            )
            
            categoria = st.selectbox(
                "Categoría *",
                options=["FIJO", "VARIABLE"],
                help="FIJO: No varía con cantidad | VARIABLE: Varía con cantidad"
            )
        
        with col2:
            st.markdown("#### 💡 Ejemplos")
            
            # Ejemplos usando solo componentes nativos de Streamlit
            st.markdown("**FIJOS:**")
            st.markdown("- Alquiler de corral")
            st.markdown("- Servicios básicos")
            st.markdown("- Mantenimiento")
            
            st.markdown("**VARIABLES:**")
            st.markdown("- Alimentación")
            st.markdown("- Transporte")
            st.markdown("- Medicamentos")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        
        with col_btn2:
            submit = st.form_submit_button(
                "✅ Crear Tipo de Costo",
                use_container_width=True,
                type="primary"
            )
        
        if submit:
            if not nombre_tipo or len(nombre_tipo.strip()) < 3:
                alert_modern("El nombre debe tener al menos 3 caracteres", "error")
            else:
                tipo_data = {
                    "nombre_tipo": nombre_tipo.strip(),
                    "categoria": categoria,
                }
                
                with st.spinner("Creando tipo de costo..."):
                    result = api.create_tipo_costo(tipo_data)
                    
                    if result["success"]:
                        alert_modern(
                            message=f"Tipo de costo '{nombre_tipo}' creado exitosamente",
                            type="success",
                            title="¡Éxito!"
                        )
                        st.balloons()
                    else:
                        error_msg = result.get("error", "Error desconocido")
                        if "exists" in error_msg.lower() or "ya existe" in error_msg.lower():
                            alert_modern("Este tipo de costo ya existe en el sistema", "error")
                        else:
                            alert_modern(f"Error: {error_msg}", "error")

# ========== INFORMACIÓN ADICIONAL ==========

st.markdown("---")
st.markdown('<div class="section-title">Sistema de Reconocimiento Automático</div>', unsafe_allow_html=True)

# Mostrar información de aliases con estilo, sin HTML crudo
st.markdown("""
<div style="
    background: linear-gradient(135deg, rgba(255, 145, 164, 0.1) 0%, rgba(255, 127, 149, 0.1) 100%);
    border: 1px solid rgba(255, 145, 164, 0.3);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 2rem;
">
    <h4 style="color: #FF91A4; margin-top: 0; display: flex; align-items: center; gap: 0.5rem;">
        <span style="font-size: 1.5rem;">🤖</span>
        <span>Aliases para Machine Learning</span>
    </h4>
    <p style="color: #E5E7EB; margin-bottom: 1rem;">
        El sistema reconoce automáticamente ciertos tipos de costo para el modelo ML:
    </p>
</div>
""", unsafe_allow_html=True)

# Contenido de aliases usando componentes nativos de Streamlit
col_al1, col_al2, col_al3 = st.columns(3)

with col_al1:
    st.markdown("**Adquisición:**")
    st.markdown("- adquisición")
    st.markdown("- compra")
    st.markdown("- precio_compra")

with col_al2:
    st.markdown("**Logística:**")
    st.markdown("- logística")
    st.markdown("- transporte")
    st.markdown("- flete")
    st.markdown("- combustible")

with col_al3:
    st.markdown("**Alimentación:**")
    st.markdown("- alimentación")
    st.markdown("- comida")
    st.markdown("- pienso")
