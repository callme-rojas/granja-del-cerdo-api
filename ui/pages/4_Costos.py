"""
Gestión de Costos - Versión Profesional Interactiva
Control financiero con visualizaciones avanzadas
"""
import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

ui_dir = Path(__file__).parent.parent
sys.path.insert(0, str(ui_dir))

from utils.auth import require_auth, get_current_user, inject_reload_warning
from utils.api_client import APIClient
from utils.advanced_charts import (
    interactive_line_chart, animated_bar_chart, interactive_donut_chart,
    kpi_gauge, display_chart, CORPORATE_COLORS
)
from utils.professional_components import (
    metric_card, alert_modern, empty_state_modern, stats_card_row
)
from utils.simple_sidebar import page_config, render_simple_sidebar
from utils.styles import inject_custom_css

# Configuración
page_config("Gestión de Costos", "💰")

require_auth()
inject_custom_css()
inject_reload_warning()

# Sidebar simple
user = get_current_user()
render_simple_sidebar("4_Costos.py", user)

# CSS profesional
st.markdown("""
<style>
    .cost-header {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(245, 158, 11, 0.3);
    }
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1F2937;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #F59E0B;
    }
</style>
""", unsafe_allow_html=True)

# API Client
api = APIClient()

# ========== HEADER ==========
st.markdown("""
<div class="cost-header">
    <h1 style="margin: 0 0 0.5rem 0; font-size: 2.5rem;">Control de Costos</h1>
    <p style="margin: 0; font-size: 1.125rem; opacity: 0.95;">Gestión financiera y análisis de gastos por lote</p>
</div>
""", unsafe_allow_html=True)

# ========== SELECCIÓN DE LOTE ==========

with st.spinner("Cargando lotes..."):
    lotes_result = api.get_lotes()
    
    if not lotes_result["success"]:
        alert_modern(
            message=f"Error al cargar lotes: {lotes_result.get('error', 'Error desconocido')}",
            type="error",
            title="Error de Conexión"
        )
        st.stop()
    
    lotes = lotes_result["data"]
    
    if not lotes:
        empty_state_modern(
            icon="🐷",
            title="No hay lotes registrados",
            description="Crea un lote primero para gestionar sus costos.",
            action_label="Ir a Lotes",
            action_callback=lambda: st.switch_page("pages/3_Lotes.py")
        )
        st.stop()

# Selector mejorado
lote_options = {}
for l in lotes:
    fecha = l.get('fecha_adquisicion', 'N/A')
    if fecha != 'N/A' and 'T' in fecha:
        fecha = fecha.split('T')[0]
    
    label = f"Número: {l['id_lote']} | {l.get('cantidad_animales', 0)} animales | {fecha}"
    lote_options[label] = l['id_lote']

selected_lote_str = st.selectbox(
    "Selecciona un lote",
    options=list(lote_options.keys()),
    key="lote_selector"
)

selected_lote_id = lote_options[selected_lote_str]

st.markdown("---")

# ========== TABS ==========

tab1, tab2, tab3 = st.tabs(["📊 Análisis de Costos", "➕ Agregar Costo", "✏️ Editar Costos"])

# ========== TAB 1: ANÁLISIS ==========

with tab1:
    st.markdown('<div class="section-title">Análisis Financiero del Lote</div>', unsafe_allow_html=True)
    
    with st.spinner("Cargando datos financieros..."):
        costos_result = api.get_costos(selected_lote_id)
        
        if costos_result["success"]:
            costos = costos_result["data"]
            
            if costos:
                df_costos = pd.DataFrame(costos)
                
                # KPIs de costos
                total_costos = float(df_costos['monto'].sum())
                costos_fijos = float(df_costos[df_costos['tipo_costo'].apply(
                    lambda x: x.get('categoria') == 'FIJO' if isinstance(x, dict) else False
                )]['monto'].sum())
                costos_variables = float(df_costos[df_costos['tipo_costo'].apply(
                    lambda x: x.get('categoria') == 'VARIABLE' if isinstance(x, dict) else False
                )]['monto'].sum())
                costo_promedio = total_costos / len(costos) if costos else 0
                
                # Métricas principales
                stats = [
                    {
                        "label": "Total Costos",
                        "value": f"Bs. {total_costos:,.2f}",
                        "icon": "💰",
                        "color": "warning"
                    },
                    {
                        "label": "Costos Fijos",
                        "value": f"Bs. {costos_fijos:,.2f}",
                        "icon": "📊",
                        "color": "primary"
                    },
                    {
                        "label": "Costos Variables",
                        "value": f"Bs. {costos_variables:,.2f}",
                        "icon": "📈",
                        "color": "success"
                    },
                    {
                        "label": "Promedio por Gasto",
                        "value": f"Bs. {costo_promedio:,.2f}",
                        "icon": "🔢",
                        "color": "info"
                    }
                ]
                
                stats_card_row(stats)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Gráficos interactivos
                col_g1, col_g2 = st.columns(2)
                
                with col_g1:
                    # Donut de distribución
                    if costos_fijos > 0 or costos_variables > 0:
                        fig1 = interactive_donut_chart(
                            labels=['Costos Fijos', 'Costos Variables'],
                            values=[costos_fijos, costos_variables],
                            title="Distribución por Categoría",
                            colors=[CORPORATE_COLORS["primary"], CORPORATE_COLORS["warning"]]
                        )
                        display_chart(fig1, key="costos_donut")
                
                with col_g2:
                    # Gauge de costos
                    # Asumiendo que el presupuesto ideal es 1.5x el total actual
                    presupuesto_ideal = total_costos * 1.5
                    porcentaje_uso = (total_costos / presupuesto_ideal * 100) if presupuesto_ideal > 0 else 0
                    
                    fig2 = kpi_gauge(
                        value=porcentaje_uso,
                        title="Uso de Presupuesto",
                        max_value=100,
                        suffix="%",
                        thresholds={"low": 50, "medium": 75}
                    )
                    display_chart(fig2, key="presupuesto_gauge")
                
                # Análisis temporal
                st.markdown('<div class="section-title">Evolución Temporal de Costos</div>', unsafe_allow_html=True)
                
                if 'fecha_gasto' in df_costos.columns:
                    df_costos['fecha_gasto'] = pd.to_datetime(df_costos['fecha_gasto'], errors='coerce')
                    df_costos = df_costos.dropna(subset=['fecha_gasto'])
                    
                    if not df_costos.empty:
                        df_costos['fecha_str'] = df_costos['fecha_gasto'].dt.strftime('%d/%m/%Y')
                        df_temporal = df_costos.groupby('fecha_str')['monto'].sum().reset_index()
                        
                        fig3 = interactive_line_chart(
                            data=df_temporal,
                            x_col='fecha_str',
                            y_cols=['monto'],
                            title="Gastos por Fecha",
                            y_title="Monto (Bs.)",
                            colors=[CORPORATE_COLORS["danger"]],
                            show_range_selector=False
                        )
                        display_chart(fig3, key="costos_temporal")
                
                # Análisis por tipo de costo
                st.markdown('<div class="section-title">Desglose por Tipo de Costo</div>', unsafe_allow_html=True)
                
                df_costos['tipo_nombre'] = df_costos['tipo_costo'].apply(
                    lambda x: x.get('nombre_tipo', 'Sin nombre') if isinstance(x, dict) else 'Sin nombre'
                )
                
                df_por_tipo = df_costos.groupby('tipo_nombre')['monto'].sum().reset_index()
                df_por_tipo = df_por_tipo.sort_values('monto', ascending=False)
                
                fig4 = animated_bar_chart(
                    data=df_por_tipo,
                    x_col='tipo_nombre',
                    y_col='monto',
                    title="Costos por Tipo",
                    orientation='h',
                    show_values=True
                )
                display_chart(fig4, key="costos_por_tipo")
                
                # Tabla detallada
                st.markdown('<div class="section-title">Detalle de Costos</div>', unsafe_allow_html=True)
                
                df_display = df_costos[['tipo_nombre', 'monto', 'fecha_gasto', 'descripcion']].copy()
                df_display['fecha_gasto'] = df_display['fecha_gasto'].dt.strftime('%d/%m/%Y')
                df_display['monto'] = df_display['monto'].apply(lambda x: f"Bs. {x:,.2f}")
                df_display['descripcion'] = df_display['descripcion'].fillna('Sin descripción')
                
                df_display.columns = ['Tipo de Costo', 'Monto', 'Fecha', 'Descripción']
                
                st.dataframe(
                    df_display,
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
                
            else:
                empty_state_modern(
                    icon="💰",
                    title="Sin costos registrados",
                    description="Este lote no tiene costos registrados. Agrega el primer costo en la pestaña 'Agregar Costo'."
                )
        else:
            alert_modern(
                message=f"Error: {costos_result.get('error', 'Error desconocido')}",
                type="error"
            )

# ========== TAB 2: AGREGAR ==========

with tab2:
    st.markdown('<div class="section-title">Registrar Nuevo Costo</div>', unsafe_allow_html=True)
    
    # Cargar tipos de costo
    tipos_result = api.get_tipos_costo()
    tipos_costo = tipos_result.get("data", []) if tipos_result.get("success") else []
    
    if not tipos_costo:
        alert_modern(
            message="No hay tipos de costo disponibles. Crea tipos de costo primero en la página 'Tipos de Costo'.",
            type="warning"
        )
    else:
        with st.form("create_costo_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📝 Información del Gasto")
                
                tipo_options = {f"{t['nombre_tipo']} ({t['categoria']})": t['id_tipo_costo'] for t in tipos_costo}
                selected_tipo_str = st.selectbox("Tipo de Costo *", options=list(tipo_options.keys()))
                selected_tipo_id = tipo_options[selected_tipo_str]
                
                monto = st.number_input("Monto (Bs.) *", min_value=0.0, value=0.0, step=0.01, format="%.2f")
                fecha_gasto = st.date_input("Fecha del Gasto *", value=datetime.now().date())
            
            with col2:
                st.markdown("#### 💬 Descripción")
                descripcion = st.text_area(
                    "Detalles del gasto",
                    placeholder="Describe el gasto (opcional)",
                    height=150
                )
                
                st.info("💡 **Tip:** Agrega descripciones detalladas para mejor seguimiento financiero")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            
            with col_btn2:
                submit = st.form_submit_button(
                    "✅ Registrar Costo",
                    use_container_width=True,
                    type="primary"
                )
            
            if submit:
                if monto <= 0:
                    alert_modern("El monto debe ser mayor a 0", "error")
                else:
                    costo_data = {
                        "id_tipo_costo": selected_tipo_id,
                        "monto": float(monto),
                        "fecha_gasto": fecha_gasto.isoformat(),
                        "descripcion": descripcion if descripcion else None,
                    }
                    
                    with st.spinner("Registrando costo..."):
                        result = api.create_costo(selected_lote_id, costo_data)
                        
                        if result["success"]:
                            alert_modern(
                                message=f"Costo registrado exitosamente: Bs. {monto:,.2f}",
                                type="success",
                                title="¡Éxito!"
                            )
                            st.balloons()
                        else:
                            alert_modern(
                                message=f"Error: {result.get('error', 'Error desconocido')}",
                                type="error"
                            )

# ========== TAB 3: EDITAR ==========

with tab3:
    st.markdown('<div class="section-title">Editar o Eliminar Costo</div>', unsafe_allow_html=True)
    
    with st.spinner("Cargando costos..."):
        costos_result = api.get_costos(selected_lote_id)
        
        if costos_result["success"]:
            costos = costos_result["data"]
            
            if costos:
                costo_options = {
                    f"Número: {c['id_costo']} - {c.get('tipo_costo', {}).get('nombre_tipo', 'N/A')} - Bs. {c.get('monto', 0):,.2f}": c['id_costo']
                    for c in costos
                }
                selected_costo_str = st.selectbox("Selecciona un costo", options=list(costo_options.keys()))
                selected_costo_id = costo_options[selected_costo_str]
                
                selected_costo = next((c for c in costos if c['id_costo'] == selected_costo_id), None)
                
                if selected_costo:
                    with st.form("edit_costo_form"):
                        st.info(f"**Editando Costo Número: {selected_costo_id}**")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            fecha_actual = selected_costo.get("fecha_gasto", datetime.now().isoformat())
                            if fecha_actual and "T" in fecha_actual:
                                fecha_actual = fecha_actual.split("T")[0]
                            try:
                                fecha_obj = datetime.strptime(fecha_actual, "%Y-%m-%d").date()
                            except:
                                fecha_obj = datetime.now().date()
                            
                            fecha_gasto = st.date_input("Fecha del Gasto", value=fecha_obj)
                            monto = st.number_input(
                                "Monto (Bs.)",
                                min_value=0.0,
                                value=float(selected_costo.get("monto", 0)),
                                step=0.01
                            )
                        
                        with col2:
                            descripcion_actual = selected_costo.get("descripcion", "")
                            descripcion = st.text_area("Descripción", value=descripcion_actual, height=100)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        col_btn1, col_btn2 = st.columns(2)
                        
                        with col_btn1:
                            update_submit = st.form_submit_button(
                                "💾 Actualizar",
                                use_container_width=True,
                                type="primary"
                            )
                        
                        with col_btn2:
                            delete_clicked = st.form_submit_button(
                                "🗑️ Eliminar",
                                use_container_width=True,
                                type="secondary"
                            )
                        
                        if update_submit:
                            if monto <= 0:
                                alert_modern("El monto debe ser mayor a 0", "error")
                            else:
                                costo_data = {
                                    "monto": float(monto),
                                    "fecha_gasto": fecha_gasto.isoformat(),
                                    "descripcion": descripcion if descripcion else None,
                                }
                                
                                with st.spinner("Actualizando..."):
                                    result = api.update_costo(selected_lote_id, selected_costo_id, costo_data)
                                    
                                    if result["success"]:
                                        alert_modern("Costo actualizado exitosamente", "success")
                                        st.rerun()
                                    else:
                                        alert_modern(f"Error: {result.get('error')}", "error")
                        
                        if delete_clicked:
                            with st.spinner("Eliminando..."):
                                result = api.delete_costo(selected_lote_id, selected_costo_id)
                                
                                if result["success"]:
                                    alert_modern("Costo eliminado exitosamente", "success")
                                    st.rerun()
                                else:
                                    alert_modern(f"Error: {result.get('error')}", "error")
            else:
                empty_state_modern(
                    icon="💰",
                    title="Sin costos para editar",
                    description="Agrega costos primero para poder editarlos."
                )
        else:
            alert_modern(f"Error: {costos_result.get('error')}", "error")
