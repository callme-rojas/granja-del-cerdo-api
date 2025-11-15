"""
Predicciones de Precios con Machine Learning - Versión Profesional
Sistema de predicción con ML y visualización profesional
"""
import streamlit as st
import sys
from pathlib import Path
import pandas as pd

ui_dir = Path(__file__).parent.parent
sys.path.insert(0, str(ui_dir))

from utils.auth import require_auth, get_current_user, inject_reload_warning
from utils.api_client import APIClient
from utils.professional_components import (
    metric_card, modern_card, badge, progress_circle,
    empty_state_modern, alert_modern, stats_card_row
)
# Componentes de navegación removidos - usando Streamlit nativo
from utils.charts import gauge_chart, bar_chart, display_chart
from utils.styles import inject_custom_css

# Configuración de página
from utils.simple_sidebar import page_config, render_simple_sidebar

page_config("Predicciones - Sistema de Gestión", "🔮")

# Autenticación y estilos
require_auth()
inject_custom_css()
inject_reload_warning()

# Sidebar simple
user = get_current_user()
render_simple_sidebar("5_Predicciones.py", user)

# Header de página
st.title("🔮 Predicción de Precios con ML")
st.caption("Obtén predicciones precisas de precios usando Machine Learning avanzado")

# API Client
api = APIClient()

# Info del modelo ML
with st.expander("ℹ️ Información del Modelo de Machine Learning", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        modern_card(
            title="Especificaciones del Modelo",
            icon="🤖",
            color="primary",
            content="""
            **Algoritmo:** LinearRegression  
            **Precisión (MAE):** 0.435 Bs/kg  
            **R² Score:** 0.934  
            **Features:** 9 variables predictoras  
            **Dataset:** 12 meses de datos sintéticos
            """
        )
    
    with col2:
        modern_card(
            title="Proceso de Predicción",
            icon="⚙️",
            color="info",
            content="""
            1. **Análisis de características** del lote  
            2. **Cálculo del precio base** usando ML  
            3. **Suma de costos fijos** por kilogramo  
            4. **Aplicación de margen** de ganancia  
            5. **Generación del precio final** sugerido
            """
        )

st.markdown("### Selección de Lote")
st.divider()

# Cargar lotes
with st.spinner("Cargando lotes disponibles..."):
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
            description="Crea un lote primero en la página de Lotes para poder generar predicciones.",
            action_label="Ir a Lotes",
            action_callback=lambda: st.switch_page("pages/3_Lotes.py")
        )
        st.stop()

# Selector de lote mejorado
lote_options = {}
for l in lotes:
    fecha = l.get('fecha_adquisicion', 'N/A')
    if fecha != 'N/A' and 'T' in fecha:
        fecha = fecha.split('T')[0]
    
    label = f"Número: {l['id_lote']} | {l.get('cantidad_animales', 0)} animales | Peso: {l.get('peso_promedio_entrada', 0):.1f} kg | {fecha}"
    lote_options[label] = l['id_lote']

selected_lote_str = st.selectbox(
    "Selecciona un lote para generar predicción",
    options=list(lote_options.keys()),
    key="predict_lote_selector"
)

selected_lote_id = lote_options[selected_lote_str]

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### Información del Lote")
st.divider()

# Cargar información del lote
with st.spinner("Cargando información del lote..."):
    features_result = api.get_lote_features(selected_lote_id, detalle=True)
    
    if not features_result["success"]:
        alert_modern(
            message=f"Error al cargar información: {features_result.get('error', 'Error desconocido')}",
            type="error",
            title="Error"
        )
        st.stop()
    
    features_data = features_result["data"]
    features = features_data.get("features", {})
    extras = features_data.get("extras", {})
    detalle = features_data.get("detalle", {})

# Mostrar métricas del lote
stats_lote = [
    {
        "label": "Cantidad Animales",
        "value": features.get("cantidad_animales", "N/A"),
        "icon": "🐖",
        "color": "primary"
    },
    {
        "label": "Peso Entrada (kg)",
        "value": f"{features.get('peso_promedio_entrada', 0):.2f}",
        "icon": "⚖️",
        "color": "success"
    },
    {
        "label": "Precio Compra (Bs/kg)",
        "value": f"{features.get('precio_compra_kg', 0):.2f}",
        "icon": "💰",
        "color": "warning"
    },
    {
        "label": "Duración (días)",
        "value": features.get("duracion_estadia_dias", "N/A"),
        "icon": "📅",
        "color": "info"
    }
]

stats_card_row(stats_lote)

st.markdown("### Análisis de Costos")
st.divider()

# Análisis de costos
col_costos1, col_costos2 = st.columns(2)

with col_costos1:
    costo_variable_total = extras.get("costo_variable_total", 0)
    
    modern_card(
        title="Costos Variables",
        icon="📈",
        color="warning",
        content=f"""
        **Total:** Bs. {costo_variable_total:,.2f}
        
        {f"**Detalle:**" if detalle.get("costos_variable") else "Sin costos registrados"}
        """
    )
    
    if detalle.get("costos_variable"):
        for costo in detalle["costos_variable"]:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"• {costo.get('tipo', 'N/A')}")
            with col2:
                badge(f"Bs. {costo.get('total', 0):,.2f}", "warning", "small")

with col_costos2:
    costo_fijo_total = extras.get("costo_fijo_total", 0)
    
    modern_card(
        title="Costos Fijos",
        icon="📊",
        color="primary",
        content=f"""
        **Total:** Bs. {costo_fijo_total:,.2f}
        
        {f"**Detalle:**" if detalle.get("costos_fijo") else "Sin costos registrados"}
        """
    )
    
    if detalle.get("costos_fijo"):
        for costo in detalle["costos_fijo"]:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"• {costo.get('tipo', 'N/A')}")
            with col2:
                badge(f"Bs. {costo.get('total', 0):,.2f}", "primary", "small")

st.markdown("### Configuración de Predicción")
st.divider()

# Configuración de margen
col_margen1, col_margen2 = st.columns([2, 1])

with col_margen1:
    margen_rate = st.slider(
        "Margen de Ganancia (%)",
        min_value=0.0,
        max_value=100.0,
        value=10.0,
        step=0.5,
        help="Porcentaje de margen de ganancia sobre el costo total"
    )
    
    # Mostrar gauge del margen
    col_gauge1, col_gauge2, col_gauge3 = st.columns([1, 2, 1])
    with col_gauge2:
        fig_gauge = gauge_chart(
            value=margen_rate,
            max_value=100,
            title="",
            color="success",
            thresholds={"low": 5, "medium": 15}
        )
        display_chart(fig_gauge)

with col_margen2:
    st.markdown("<br>" * 2, unsafe_allow_html=True)
    modern_card(
        title="Información del Margen",
        icon="💡",
        color="info",
        content=f"""
        **Margen Seleccionado:** {margen_rate}%
        
        El precio sugerido incluirá este margen sobre el costo total del lote.
        
        **Recomendaciones:**
        - Bajo (0-10%): Competitivo
        - Medio (10-20%): Equilibrado
        - Alto (>20%): Premium
        """
    )

st.markdown("<br>", unsafe_allow_html=True)

# Botón de predicción
col_predict1, col_predict2, col_predict3 = st.columns([1, 2, 1])

with col_predict2:
    if st.button("🔮 Generar Predicción con ML", use_container_width=True, type="primary"):
        with st.spinner("Generando predicción con Machine Learning..."):
            margen_decimal = margen_rate / 100.0
            
            predict_result = api.predict_lote(selected_lote_id, margen_decimal)
            
            if predict_result["success"]:
                prediction = predict_result["data"]
                
                st.success("✅ Predicción generada exitosamente")
                st.balloons()
                
                st.markdown("### Resultados de la Predicción")
                st.divider()
                
                # Métricas principales de predicción
                st.markdown("### 📊 Resultados Principales")
                
                col_r1, col_r2, col_r3, col_r4 = st.columns(4)
                
                with col_r1:
                    precio_base = prediction.get("precio_base_kg", 0)
                    metric_card(
                        label="Precio Base ML",
                        value=f"{precio_base:.4f}",
                        icon="🤖",
                        color="primary"
                    )
                    st.caption("Predicción del modelo")
                
                with col_r2:
                    fijo_por_kg = prediction.get("fijo_por_kg", 0)
                    metric_card(
                        label="Fijo por kg",
                        value=f"{fijo_por_kg:.4f}",
                        icon="📊",
                        color="warning"
                    )
                    st.caption("Costos fijos / kg")
                
                with col_r3:
                    precio_sugerido = prediction.get("precio_sugerido_kg", 0)
                    metric_card(
                        label="Precio Sugerido",
                        value=f"{precio_sugerido:.4f}",
                        icon="💰",
                        color="success",
                        delta=f"+{margen_rate}%",
                        delta_color="positive"
                    )
                    st.caption("Precio final con margen")
                
                with col_r4:
                    ganancia_neta = prediction.get("ganancia_neta_estimada", 0)
                    metric_card(
                        label="Ganancia Neta",
                        value=f"{ganancia_neta:,.2f}",
                        icon="💵",
                        color="info"
                    )
                    st.caption("Bs.")
                
                st.markdown("### Desglose Detallado")
                st.divider()
                
                # Tabla de desglose
                st.markdown("### 📋 Desglose de Cálculo")
                
                desglose_data = {
                    "Concepto": [
                        "Precio Base (ML)",
                        "Costos Fijos por kg",
                        "Subtotal",
                        f"Margen ({margen_rate}%)",
                        "Precio Sugerido Final"
                    ],
                    "Valor (Bs/kg)": [
                        f"{precio_base:.4f}",
                        f"{fijo_por_kg:.4f}",
                        f"{precio_base + fijo_por_kg:.4f}",
                        f"{(precio_base + fijo_por_kg) * margen_decimal:.4f}",
                        f"{precio_sugerido:.4f}"
                    ],
                    "Estado": [
                        "✓", "✓", "✓", "✓", "✓"
                    ]
                }
                
                df_desglose = pd.DataFrame(desglose_data)
                st.dataframe(df_desglose, use_container_width=True, hide_index=True)
                
                # Información adicional
                st.markdown("### Información Adicional")
                st.divider()
                
                col_info1, col_info2 = st.columns(2)
                
                with col_info1:
                    modern_card(
                        title="Datos de la Predicción",
                        icon="🔍",
                        color="primary",
                        content=f"""
                        **Número de Predicción:** {prediction.get('prediccion_id', 'N/A')}  
                        **Número del Lote:** {prediction.get('lote_id', 'N/A')}  
                        **Modelo:** LinearRegression  
                        **Precisión:** 93.4% (R²)
                        """
                    )
                
                with col_info2:
                    peso_salida = extras.get("peso_salida_total", 0)
                    ingreso_total = precio_sugerido * peso_salida if peso_salida > 0 else 0
                    costo_total = costo_variable_total + costo_fijo_total
                    
                    modern_card(
                        title="Proyección Financiera",
                        icon="💰",
                        color="success",
                        content=f"""
                        **Peso Salida Total:** {peso_salida:.2f} kg  
                        **Ingreso Total Estimado:** Bs. {ingreso_total:,.2f}  
                        **Costo Total:** Bs. {costo_total:,.2f}  
                        **ROI:** {(ganancia_neta / costo_total * 100) if costo_total > 0 else 0:.2f}%
                        """
                    )
                
                # Gráfico de comparación
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### 📈 Visualización Comparativa")
                
                df_comparacion = pd.DataFrame({
                    'Componente': ['Precio Base', 'Costos Fijos/kg', 'Margen', 'Precio Final'],
                    'Valor': [
                        precio_base,
                        fijo_por_kg,
                        (precio_base + fijo_por_kg) * margen_decimal,
                        precio_sugerido
                    ]
                })
                
                fig_comp = bar_chart(
                    data=df_comparacion,
                    x_col='Componente',
                    y_col='Valor',
                    title="Composición del Precio Sugerido (Bs/kg)",
                    color="gradient",
                    show_values=True
                )
                display_chart(fig_comp)
                
                # Datos completos en expander
                with st.expander("🔬 Ver Datos Completos de la Predicción (JSON)"):
                    st.json(prediction)
                
            else:
                error_msg = predict_result.get("error", "Error desconocido")
                alert_modern(
                    message=f"Error al generar predicción: {error_msg}",
                    type="error",
                    title="Error en la Predicción"
                )
                
                if "lote_not_found" in error_msg.lower():
                    st.info("💡 Asegúrate de que el lote tenga todos los datos necesarios (cantidad de animales, peso, precio de compra, etc.)")
                elif "modelo" in error_msg.lower() or "model" in error_msg.lower():
                    st.warning("⚠️ El modelo ML no está disponible. Verifica que el archivo del modelo esté en la ubicación correcta en el servidor.")
