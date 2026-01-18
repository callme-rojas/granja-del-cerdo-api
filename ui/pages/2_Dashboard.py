"""
Dashboard Profesional Interactivo
Vista analítica avanzada con gráficos interactivos de Plotly    
"""
import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging

ui_dir = Path(__file__).parent.parent
sys.path.insert(0, str(ui_dir))

from utils.auth import require_auth, get_current_user, inject_reload_warning
from utils.api_client import APIClient
from utils.advanced_charts import (
    interactive_line_chart, animated_bar_chart, interactive_donut_chart,
    multi_axis_chart, scatter_with_regression, comparison_chart,
    kpi_gauge, display_chart, CORPORATE_COLORS
)
from utils.styles import inject_custom_css
# Configuración de página
from utils.simple_sidebar import page_config, render_simple_sidebar

page_config("Dashboard Analítico", "📊")

require_auth()
inject_custom_css()
inject_reload_warning()

# Sidebar simple nativo
user = get_current_user()
render_simple_sidebar("2_Dashboard.py", user)

# Instrumentación de rendimiento
logger = logging.getLogger("dashboard_perf")
perf = st.session_state.setdefault("perf_dashboard", {})
perf.clear()
perf["start"] = time.perf_counter()
logger.info("Dashboard perf - inicio de ejecución")

# CSS adicional para dashboard profesional
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #0A0A0A 0%, #1A1A2E 100%);
        padding: 1.5rem;
        border-radius: 16px;
        border: 2px solid #3A3A4A;
        box-shadow: 0 4px 20px rgba(255, 145, 164, 0.15);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #FF91A4, #FFB6C1);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 40px rgba(255, 145, 164, 0.3);
        border-color: #FF91A4;
    }
    .metric-card:hover::before {
        opacity: 1;
    }
    .metric-value {
        font-size: 2.75rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FFFFFF 0%, #E0E0E0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1;
        margin: 0.5rem 0;
        letter-spacing: -0.5px;
    }
    .metric-label {
        font-size: 0.875rem;
        font-weight: 600;
        color: #B0B0B0;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    .metric-delta {
        font-size: 0.875rem;
        font-weight: 600;
        margin-top: 0.75rem;
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
    }
    .delta-positive { 
        color: #A8E6CF; 
        background: rgba(168, 230, 207, 0.1);
    }
    .delta-negative { 
        color: #FF9AA2; 
        background: rgba(255, 154, 162, 0.1);
    }
    .section-header {
        font-size: 1.75rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 3rem 0 1.5rem 0;
        padding-bottom: 1rem;
        border-bottom: 3px solid transparent;
        border-image: linear-gradient(90deg, #FF91A4, #FFB6C1) 1;
        position: relative;
    }
    .section-header::after {
        content: '';
        position: absolute;
        bottom: -3px;
        left: 0;
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, #FF91A4, #FFB6C1);
        border-radius: 2px;
    }
</style>
""", unsafe_allow_html=True)

# API Client
api = APIClient()


# ========== HEADER ==========
col_header1, col_header2 = st.columns([4, 1])

with col_header1:
    st.markdown('<h1 style="color: #FFFFFF; margin-bottom: 0;">📊 Dashboard Analítico</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #B0B0B0; font-size: 1.125rem;">Análisis avanzado de producción y rendimiento</p>', unsafe_allow_html=True)

with col_header2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⟳ Actualizar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# ========== FUNCIONES DE DATOS ==========

@st.cache_data(ttl=300)
def get_dashboard_data():
    """Obtiene todos los datos consolidados del dashboard desde el backend."""
    overview_result = api.get_dashboard_overview()
    if overview_result.get("success"):
        data = overview_result.get("data") or {}
        lotes = data.get("lotes") or []
        costos = data.get("costos") or []
        return {"lotes": lotes, "costos": costos}

    logging.error("Dashboard perf - error al obtener overview: %s", overview_result.get("error"))
    return {"lotes": [], "costos": []}


def process_data(data):
    """Procesa y transforma los datos"""
    lotes = data["lotes"]
    costos = data["costos"]
    
    if not lotes:
        return None
    
    df_lotes = pd.DataFrame(lotes)
    df_costos = pd.DataFrame(costos) if costos else pd.DataFrame()
    
    # Procesar fechas
    if not df_lotes.empty:
        df_lotes['fecha_adquisicion'] = pd.to_datetime(df_lotes['fecha_adquisicion'], errors='coerce')
        df_lotes = df_lotes.dropna(subset=['fecha_adquisicion'])
        df_lotes['mes'] = df_lotes['fecha_adquisicion'].dt.to_period('M').astype(str)
        df_lotes['mes_dt'] = df_lotes['fecha_adquisicion'].dt.to_period('M').dt.to_timestamp()
        df_lotes['año'] = df_lotes['fecha_adquisicion'].dt.year
        df_lotes['trimestre'] = df_lotes['fecha_adquisicion'].dt.quarter
    
    if not df_costos.empty and 'fecha_gasto' in df_costos.columns:
        df_costos['fecha_gasto'] = pd.to_datetime(df_costos['fecha_gasto'], errors='coerce')
        df_costos = df_costos.dropna(subset=['fecha_gasto'])
        df_costos['mes'] = df_costos['fecha_gasto'].dt.to_period('M').astype(str)
        df_costos['mes_dt'] = df_costos['fecha_gasto'].dt.to_period('M').dt.to_timestamp()
    
    return {"lotes": df_lotes, "costos": df_costos}


# ========== CARGAR DATOS ==========

with st.spinner("Cargando datos..."):
    fetch_start = time.perf_counter()
    raw_data = get_dashboard_data()
    perf["data_fetch_s"] = time.perf_counter() - fetch_start
    logger.info("Dashboard perf - data_fetch_s: %.3fs", perf["data_fetch_s"])
    
    if not raw_data["lotes"]:
        st.info("📋 No hay datos disponibles. Crea lotes para ver el análisis.")
        st.stop()
    
    process_start = time.perf_counter()
    processed_data = process_data(raw_data)
    perf["data_process_s"] = time.perf_counter() - process_start
    logger.info("Dashboard perf - data_process_s: %.3fs", perf["data_process_s"])
    
    if processed_data is None:
        st.error("Error al procesar datos")
        st.stop()
    
    df_lotes = processed_data["lotes"]
    df_costos = processed_data["costos"]

perf["data_pipeline_s"] = time.perf_counter() - perf["start"]
logger.info("Dashboard perf - data_pipeline_s: %.3fs", perf["data_pipeline_s"])

# ========== PANEL DE FILTROS ==========

# Título de filtros con estilo
st.markdown("""
<div style="color: #FFFFFF; font-size: 1.125rem; font-weight: 600; margin-bottom: 1.5rem; padding-bottom: 0.75rem; border-bottom: 2px solid rgba(255, 145, 164, 0.3);">
    🔍 Filtros de Análisis
</div>
""", unsafe_allow_html=True)

# Filtros en columnas
col_f1, col_f2, col_f3, col_f4 = st.columns(4)

with col_f1:
    años_disponibles = sorted(df_lotes['año'].unique(), reverse=True)
    año_selected = st.selectbox("Año", ["Todos"] + list(años_disponibles), key="filter_año")

with col_f2:
    trimestre_selected = st.selectbox("Trimestre", ["Todos", "Q1", "Q2", "Q3", "Q4"], key="filter_trimestre")

with col_f3:
    min_animales = st.number_input("Mín. Animales", min_value=0, value=0, key="filter_min_animales")

with col_f4:
    periodo = st.selectbox("Período", ["Últimos 3 meses", "Últimos 6 meses", "Último año", "Todo"], key="filter_periodo")

st.markdown("<br>", unsafe_allow_html=True)

# Aplicar filtros
df_filtered = df_lotes.copy()

if año_selected != "Todos":
    df_filtered = df_filtered[df_filtered['año'] == año_selected]

if trimestre_selected != "Todos":
    q_num = int(trimestre_selected[1])
    df_filtered = df_filtered[df_filtered['trimestre'] == q_num]

if min_animales > 0:
    df_filtered = df_filtered[df_filtered['cantidad_animales'] >= min_animales]

if periodo != "Todo":
    fecha_limite = datetime.now()
    if periodo == "Últimos 3 meses":
        fecha_limite = fecha_limite - timedelta(days=90)
    elif periodo == "Últimos 6 meses":
        fecha_limite = fecha_limite - timedelta(days=180)
    elif periodo == "Último año":
        fecha_limite = fecha_limite - timedelta(days=365)
    
    df_filtered = df_filtered[df_filtered['fecha_adquisicion'] >= fecha_limite]

# ========== KPIs PRINCIPALES ==========

st.markdown('<div class="section-header">Indicadores Clave de Rendimiento</div>', unsafe_allow_html=True)

col_k1, col_k2, col_k3, col_k4 = st.columns(4)
kpi_start = time.perf_counter()

total_lotes = len(df_filtered)
total_animales = int(df_filtered['cantidad_animales'].sum())
peso_promedio = float(df_filtered['peso_promedio_entrada'].mean())
inversion_total = float(df_filtered['precio_compra_kg'].sum() * df_filtered['peso_promedio_entrada'].sum()) if 'precio_compra_kg' in df_filtered.columns else 0

# Calcular deltas comparando con período anterior
if len(df_filtered) > 0:
    fecha_media = df_filtered['fecha_adquisicion'].median()
    df_antes = df_lotes[df_lotes['fecha_adquisicion'] < fecha_media]
    df_despues = df_lotes[df_lotes['fecha_adquisicion'] >= fecha_media]
    
    delta_lotes = ((len(df_despues) - len(df_antes)) / len(df_antes) * 100) if len(df_antes) > 0 else 0
    delta_animales = ((df_despues['cantidad_animales'].sum() - df_antes['cantidad_animales'].sum()) / df_antes['cantidad_animales'].sum() * 100) if len(df_antes) > 0 else 0
else:
    delta_lotes = 0
    delta_animales = 0

with col_k1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Lotes</div>
        <div class="metric-value">{total_lotes:,}</div>
        <div class="metric-delta {'delta-positive' if delta_lotes >= 0 else 'delta-negative'}">
            {'▲' if delta_lotes >= 0 else '▼'} {abs(delta_lotes):.2f}%
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_k2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Animales</div>
        <div class="metric-value">{total_animales:,}</div>
        <div class="metric-delta {'delta-positive' if delta_animales >= 0 else 'delta-negative'}">
            {'▲' if delta_animales >= 0 else '▼'} {abs(delta_animales):.2f}%
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_k3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Peso Promedio</div>
        <div class="metric-value">{peso_promedio:.2f}<span style="font-size:1.5rem"> kg</span></div>
        <div class="metric-delta">Por animal</div>
    </div>
    """, unsafe_allow_html=True)

with col_k4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Inversión Total</div>
        <div class="metric-value">Bs. {inversion_total:,.0f}</div>
        <div class="metric-delta">Acumulado</div>
    </div>
    """, unsafe_allow_html=True)

perf["kpi_render_s"] = time.perf_counter() - kpi_start
logger.info("Dashboard perf - kpi_render_s: %.3fs", perf["kpi_render_s"])

# ========== GRÁFICOS INTERACTIVOS PRINCIPALES ==========

st.markdown('<div class="section-header">Análisis de Tendencias Temporales</div>', unsafe_allow_html=True)

col_g1, col_g2 = st.columns(2)

with col_g1:
    # Gráfico de líneas interactivo con múltiples métricas
    if not df_filtered.empty:
        chart_temporal_start = time.perf_counter()
        df_temporal = df_filtered.groupby('mes_dt').agg({
            'cantidad_animales': 'sum',
            'id_lote': 'count'
        }).reset_index()
        df_temporal.columns = ['Fecha', 'Total Animales', 'Cantidad Lotes']
        
        fig1 = interactive_line_chart(
            data=df_temporal,
            x_col='Fecha',
            y_cols=['Total Animales', 'Cantidad Lotes'],
            title="Evolución de Lotes y Animales",
            y_title="Cantidad",
            show_range_selector=True
        )
        display_chart(fig1, key="chart_temporal")
        perf["chart_temporal_s"] = time.perf_counter() - chart_temporal_start
        logger.info("Dashboard perf - chart_temporal_s: %.3fs", perf["chart_temporal_s"])

with col_g2:
    # Gráfico de barras animado
    if not df_filtered.empty:
        chart_barras_start = time.perf_counter()
        df_barras = df_filtered.groupby('mes_dt').agg({
            'cantidad_animales': 'sum'
        }).reset_index().tail(12)
        df_barras['mes_nombre'] = df_barras['mes_dt'].dt.strftime('%b %Y')
        
        fig2 = animated_bar_chart(
            data=df_barras,
            x_col='mes_nombre',
            y_col='cantidad_animales',
            title="Distribución Mensual de Animales",
            show_values=True
        )
        display_chart(fig2, key="chart_barras")
        perf["chart_barras_s"] = time.perf_counter() - chart_barras_start
        logger.info("Dashboard perf - chart_barras_s: %.3fs", perf["chart_barras_s"])

# ========== ANÁLISIS DE COSTOS ==========

st.markdown('<div class="section-header">Análisis Financiero y Costos</div>', unsafe_allow_html=True)

col_c1, col_c2 = st.columns([1, 1])

with col_c1:
    # Donut chart interactivo de costos
    if not df_costos.empty:
        chart_donut_start = time.perf_counter()
        costos_fijos = float(df_costos[df_costos['tipo_costo'].apply(
            lambda x: x.get('categoria') == 'FIJO' if isinstance(x, dict) else False
        )]['monto'].sum())
        
        costos_variables = float(df_costos[df_costos['tipo_costo'].apply(
            lambda x: x.get('categoria') == 'VARIABLE' if isinstance(x, dict) else False
        )]['monto'].sum())
        
        if costos_fijos > 0 or costos_variables > 0:
            fig3 = interactive_donut_chart(
                labels=['Costos Fijos', 'Costos Variables'],
                values=[costos_fijos, costos_variables],
                title="Distribución de Costos por Categoría",
                colors=[CORPORATE_COLORS["primary"], CORPORATE_COLORS["warning"]]
            )
            display_chart(fig3, key="chart_costos_donut")
            perf["chart_costos_donut_s"] = time.perf_counter() - chart_donut_start
            logger.info("Dashboard perf - chart_costos_donut_s: %.3fs", perf["chart_costos_donut_s"])

with col_c2:
    # Gráfico de evolución de costos
    if not df_costos.empty:
        chart_costos_line_start = time.perf_counter()
        df_costos_tiempo = df_costos.groupby('mes_dt')['monto'].sum().reset_index()
        df_costos_tiempo = df_costos_tiempo.tail(12)
        df_costos_tiempo['mes_nombre'] = df_costos_tiempo['mes_dt'].dt.strftime('%b %Y')
        
        fig4 = interactive_line_chart(
            data=df_costos_tiempo,
            x_col='mes_nombre',
            y_cols=['monto'],
            title="Evolución Temporal de Costos",
            y_title="Monto (Bs.)",
            colors=[CORPORATE_COLORS["danger"]],
            show_range_selector=False
        )
        display_chart(fig4, key="chart_costos_evol")
        perf["chart_costos_evol_s"] = time.perf_counter() - chart_costos_line_start
        logger.info("Dashboard perf - chart_costos_evol_s: %.3fs", perf["chart_costos_evol_s"])

# ========== ANÁLISIS COMPARATIVO ==========

st.markdown('<div class="section-header">Análisis Comparativo Multieje</div>', unsafe_allow_html=True)

if not df_filtered.empty and 'precio_compra_kg' in df_filtered.columns:
    df_precios = df_filtered[df_filtered['precio_compra_kg'].notna() & (df_filtered['precio_compra_kg'] > 0)]
    
    if not df_precios.empty:
        chart_multi_axis_start = time.perf_counter()
        df_comparativo = df_filtered.groupby('mes_dt').agg({
            'cantidad_animales': 'sum',
            'precio_compra_kg': 'mean',
            'peso_promedio_entrada': 'mean'
        }).reset_index().tail(12)
        df_comparativo['mes_nombre'] = df_comparativo['mes_dt'].dt.strftime('%b %Y')
        
        fig5 = multi_axis_chart(
            data=df_comparativo,
            x_col='mes_nombre',
            y1_cols=['cantidad_animales'],
            y2_cols=['precio_compra_kg'],
            title="Cantidad de Animales vs Precio de Compra",
            y1_title="Total Animales",
            y2_title="Precio (Bs/kg)"
        )
        display_chart(fig5, key="chart_multi_axis")
        perf["chart_multi_axis_s"] = time.perf_counter() - chart_multi_axis_start
        logger.info("Dashboard perf - chart_multi_axis_s: %.3fs", perf["chart_multi_axis_s"])

# ========== ANÁLISIS DE CORRELACIÓN ==========

st.markdown('<div class="section-header">Análisis de Correlación</div>', unsafe_allow_html=True)

col_s1, col_s2 = st.columns(2)

with col_s1:
    # Scatter plot con regresión
    if not df_filtered.empty and len(df_filtered) > 2:
        chart_scatter_start = time.perf_counter()
        df_scatter = df_filtered[['peso_promedio_entrada', 'cantidad_animales', 'precio_compra_kg']].copy()
        df_scatter = df_scatter[df_scatter['precio_compra_kg'].notna()]
        
        if len(df_scatter) > 2:
            fig6 = scatter_with_regression(
                data=df_scatter,
                x_col='peso_promedio_entrada',
                y_col='precio_compra_kg',
                title="Correlación: Peso vs Precio de Compra",
                size_col='cantidad_animales'
            )
            display_chart(fig6, key="chart_scatter")
            perf["chart_scatter_s"] = time.perf_counter() - chart_scatter_start
            logger.info("Dashboard perf - chart_scatter_s: %.3fs", perf["chart_scatter_s"])

with col_s2:
    # Comparación trimestral
    if not df_filtered.empty and 'trimestre' in df_filtered.columns:
        chart_comparison_start = time.perf_counter()
        df_trimestral = df_filtered.groupby('trimestre').agg({
            'cantidad_animales': 'sum',
            'peso_promedio_entrada': 'mean'
        }).reset_index()
        df_trimestral['trimestre_label'] = 'Q' + df_trimestral['trimestre'].astype(str)
        
        series_dict = {
            'Total Animales': df_trimestral['cantidad_animales'].tolist(),
            'Peso Promedio': (df_trimestral['peso_promedio_entrada'] * 10).tolist()  # Escalar para visualización
        }
        
        fig7 = comparison_chart(
            categories=df_trimestral['trimestre_label'].tolist(),
            series_data=series_dict,
            title="Comparación por Trimestre",
            chart_type='bar'
        )
        display_chart(fig7, key="chart_comparison")
        perf["chart_comparison_s"] = time.perf_counter() - chart_comparison_start
        logger.info("Dashboard perf - chart_comparison_s: %.3fs", perf["chart_comparison_s"])

# ========== GAUGES DE RENDIMIENTO ==========

st.markdown('<div class="section-header">Indicadores de Rendimiento</div>', unsafe_allow_html=True)

col_gauge1, col_gauge2, col_gauge3 = st.columns(3)

with col_gauge1:
    # Eficiencia de peso (referencia: 90 kg - peso óptimo para cerdos de reventa)
    eficiencia_peso = (peso_promedio / 90) * 100 if peso_promedio > 0 else 0
    gauge_peso_start = time.perf_counter()
    fig_g1 = kpi_gauge(
        value=min(eficiencia_peso, 100),
        title="Eficiencia de Peso",
        max_value=100,
        suffix="%"
    )
    display_chart(fig_g1, key="gauge_peso")
    perf["gauge_peso_s"] = time.perf_counter() - gauge_peso_start
    logger.info("Dashboard perf - gauge_peso_s: %.3fs", perf["gauge_peso_s"])

with col_gauge2:
    # Ocupación
    ocupacion = (total_animales / (total_lotes * 15)) * 100 if total_lotes > 0 else 0
    gauge_ocupacion_start = time.perf_counter()
    fig_g2 = kpi_gauge(
        value=min(ocupacion, 100),
        title="Ocupación Promedio",
        max_value=100,
        suffix="%",
        thresholds={"low": 40, "medium": 70}
    )
    display_chart(fig_g2, key="gauge_ocupacion")
    perf["gauge_ocupacion_s"] = time.perf_counter() - gauge_ocupacion_start
    logger.info("Dashboard perf - gauge_ocupacion_s: %.3fs", perf["gauge_ocupacion_s"])

with col_gauge3:
    # Crecimiento
    crecimiento = min(abs(delta_lotes), 100)
    gauge_crecimiento_start = time.perf_counter()
    fig_g3 = kpi_gauge(
        value=crecimiento,
        title="Crecimiento",
        max_value=100,
        suffix="%",
        thresholds={"low": 10, "medium": 30}
    )
    display_chart(fig_g3, key="gauge_crecimiento")
    perf["gauge_crecimiento_s"] = time.perf_counter() - gauge_crecimiento_start
    logger.info("Dashboard perf - gauge_crecimiento_s: %.3fs", perf["gauge_crecimiento_s"])

# ========== TABLA DE DATOS ==========

st.markdown('<div class="section-header">Datos Detallados</div>', unsafe_allow_html=True)

if not df_filtered.empty:
    table_start = time.perf_counter()
    df_display = df_filtered[[
        'id_lote', 'fecha_adquisicion', 'cantidad_animales',
        'peso_promedio_entrada', 'precio_compra_kg', 'duracion_estadia_dias'
    ]].copy()
    
    df_display['fecha_adquisicion'] = df_display['fecha_adquisicion'].dt.strftime('%d/%m/%Y')
    df_display['precio_compra_kg'] = df_display['precio_compra_kg'].fillna(0).apply(lambda x: f"Bs. {x:.2f}")
    df_display['peso_promedio_entrada'] = df_display['peso_promedio_entrada'].apply(lambda x: f"{x:.2f} kg")
    df_display['duracion_estadia_dias'] = df_display['duracion_estadia_dias'].fillna(0).apply(lambda x: f"{int(x)} días")
    
    df_display.columns = ['Número del Lote', 'Fecha', 'Animales', 'Peso Promedio', 'Precio/kg', 'Duración']
    
    st.dataframe(
        df_display.sort_values('Número del Lote', ascending=False).head(20),
        use_container_width=True,
        hide_index=True,
        height=400
    )
    perf["table_render_s"] = time.perf_counter() - table_start
    logger.info("Dashboard perf - table_render_s: %.3fs", perf["table_render_s"])
else:
    st.info("No hay datos que coincidan con los filtros seleccionados")

# ========== FOOTER ==========

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
col_footer1, col_footer2, col_footer3 = st.columns(3)

with col_footer1:
    st.markdown(f"**Total registros analizados:** {len(df_filtered)}")
with col_footer2:
    st.markdown(f"**Período:** {df_filtered['fecha_adquisicion'].min().strftime('%d/%m/%Y') if not df_filtered.empty else 'N/A'} - {df_filtered['fecha_adquisicion'].max().strftime('%d/%m/%Y') if not df_filtered.empty else 'N/A'}")
with col_footer3:
    st.markdown(f"**Última actualización:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")

perf["total_elapsed_s"] = time.perf_counter() - perf["start"]
logger.info("Dashboard perf - total_elapsed_s: %.3fs", perf["total_elapsed_s"])

# Mostrar métricas de rendimiento
st.markdown("---")
with st.expander("⚙️ Métricas de rendimiento (debug)", expanded=False):
    if not perf or len(perf) <= 1:
        st.info("Sin métricas registradas aún.")
    else:
        # Crear tabla de métricas
        metrics_data = []
        for metric in sorted(perf.keys()):
            if metric == "start":
                continue
            value = perf[metric]
            if isinstance(value, (int, float)):
                metrics_data.append({
                    "Métrica": metric.replace("_", " ").title(),
                    "Tiempo (s)": f"{value:.2f}",
                    "Estado": "✅" if value < 1.0 else "⚠️" if value < 3.0 else "❌"
                })
        
        if metrics_data:
            df_metrics = pd.DataFrame(metrics_data)
            st.dataframe(df_metrics, use_container_width=True, hide_index=True)
            
            # Resumen
            total_time = perf.get("total_elapsed_s", 0)
            fetch_time = perf.get("data_fetch_s", 0)
            st.markdown(f"""
            **Resumen:**
            - ⏱️ Tiempo total: **{total_time:.2f}s**
            - 📥 Carga de datos: **{fetch_time:.2f}s** ({fetch_time/total_time*100:.2f}% del total)
            - ✅ Objetivo: < 1.5s (First Contentful Paint)
            """)
        else:
            st.info("No hay métricas numéricas para mostrar.")
