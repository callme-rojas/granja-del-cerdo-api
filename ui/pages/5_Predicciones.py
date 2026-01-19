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
    empty_state_modern, alert_modern, stats_card_row,
    stats_card_responsive, responsive_grid
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
with st.expander("ℹ️ Información del Modelo de Machine Learning XGBoost", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        # Card de especificaciones usando HTML directo
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(255, 145, 164, 0.1) 0%, rgba(255, 127, 149, 0.1) 100%);
            border: 1px solid rgba(255, 145, 164, 0.3);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        ">
            <h4 style="color: #FF91A4; margin-top: 0; display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.5rem;">🤖</span>
                <span>Especificaciones del Modelo</span>
            </h4>
            <div style="color: #E5E7EB; margin-top: 1rem; line-height: 1.7;">
                <strong>Algoritmo:</strong> XGBoost (Extreme Gradient Boosting)<br>
                <strong>Precisión (MAE):</strong> 0.59 ± 0.02 Bs/kg<br>
                <strong>R² Score:</strong> 0.91 (91% varianza explicada)<br>
                <strong>Features:</strong> 24 variables predictoras<br>
                <strong>Dataset:</strong> 2000 lotes sintéticos<br>
                <strong>Versión:</strong> v1.0
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Card de proceso usando HTML directo
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        ">
            <h4 style="color: #60A5FA; margin-top: 0; display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.5rem;">⚙️</span>
                <span>Proceso de Predicción</span>
            </h4>
            <div style="color: #E5E7EB; margin-top: 1rem; line-height: 1.7;">
                <strong>1.</strong> Análisis de 24 características del lote<br>
                <strong>2.</strong> Consulta de feriados próximos (estacionalidad)<br>
                <strong>3.</strong> Prorrateo dinámico de costos indirectos<br>
                <strong>4.</strong> Cálculo de variables compuestas<br>
                <strong>5.</strong> Predicción con XGBoost entrenado
            </div>
        </div>
        """, unsafe_allow_html=True)


st.markdown("### Selección de Lote")
st.divider()

# Opciones de selección: por lista o por número
col_sel1, col_sel2 = st.columns([2, 1])

with col_sel1:
    metodo_seleccion = st.radio(
        "Método de selección",
        ["Seleccionar de la lista", "Buscar por número"],
        horizontal=True,
        key="metodo_seleccion_lote"
    )

selected_lote_id = None

if metodo_seleccion == "Seleccionar de la lista":
    # Cargar lotes (últimos 50)
    with st.spinner("Cargando lotes disponibles..."):
        lotes_result = api.get_lotes(limit=50)
        
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
        if fecha != 'N/A':
            if isinstance(fecha, str):
                if 'T' in fecha:
                    fecha = fecha.split('T')[0]
                elif ' ' in fecha:
                    fecha = fecha.split(' ')[0]
            elif isinstance(fecha, datetime):
                fecha = fecha.strftime("%Y-%m-%d")
        
        label = f"Número: {l['id_lote']} | {l.get('cantidad_animales', 0)} animales | Peso: {l.get('peso_promedio_entrada', 0):.2f} kg | {fecha}"
        lote_options[label] = l['id_lote']

    selected_lote_str = st.selectbox(
        "Selecciona un lote para generar predicción (últimos 50 lotes)",
        options=list(lote_options.keys()),
        key="predict_lote_selector"
    )

    selected_lote_id = lote_options[selected_lote_str]

else:
    # Búsqueda por número de lote
    with col_sel2:
        st.markdown("<br>", unsafe_allow_html=True)
    
    numero_lote = st.number_input(
        "Ingresa el número de lote",
        min_value=1,
        step=1,
        key="buscar_lote_numero"
    )
    
    if numero_lote:
        selected_lote_id = numero_lote
    else:
        st.info("Ingresa un número de lote para continuar")
        st.stop()

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

stats_card_responsive(stats_lote, min_col_width_px=260, gap="1rem")

st.markdown("### Análisis de Costos")
st.divider()

# Análisis de costos (responsive)
# IMPORTANTE: costo_variable_total incluye la compra de animales
# Para mostrar solo costos variables de BD, restamos la compra
total_adquisicion = extras.get("total_adquisicion", 0)
costo_variable_total_con_compra = extras.get("costo_variable_total", 0)
costo_variable_solo_bd = costo_variable_total_con_compra - total_adquisicion  # Solo costos variables de BD

detalle_text_var = ""
por_tipo_variable = detalle.get("por_tipo_variable", {})
if por_tipo_variable:
    detalle_text_var = "<strong>Detalle:</strong><br>"
    for tipo, monto in por_tipo_variable.items():
        if monto > 0:
            detalle_text_var += f"• {tipo}: Bs. {monto:,.2f}<br>"
else:
    detalle_text_var = "Sin costos variables registrados"

card_variables = f"""
<div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.1) 100%); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem;">
    <h4 style="color: #FBBF24; margin-top: 0; display: flex; align-items: center; gap: 0.5rem;">
        <span style="font-size: 1.5rem;">📈</span>
        <span>Costos Variables</span>
    </h4>
    <div style="color: #E5E7EB; margin-top: 1rem; line-height: 1.7;">
        <strong>Total:</strong> Bs. {costo_variable_solo_bd:,.2f}<br>
        <small style="color: #9CA3AF;">(Solo costos variables de BD, sin incluir compra de animales)</small><br><br>
        {detalle_text_var}
    </div>
</div>
"""

costo_fijo_total = extras.get("costo_fijo_total", 0)
detalle_text_fijo = ""
por_tipo_fijo = detalle.get("por_tipo_fijo", {})
if por_tipo_fijo:
    detalle_text_fijo = "<strong>Detalle:</strong><br>"
    for tipo, monto in por_tipo_fijo.items():
        if monto > 0:
            detalle_text_fijo += f"• {tipo}: Bs. {monto:,.2f}<br>"
else:
    detalle_text_fijo = "Sin costos fijos registrados"

card_fijos = f"""
<div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem;">
    <h4 style="color: #60A5FA; margin-top: 0; display: flex; align-items: center; gap: 0.5rem;">
        <span style="font-size: 1.5rem;">📊</span>
        <span>Costos Fijos</span>
    </h4>
    <div style="color: #E5E7EB; margin-top: 1rem; line-height: 1.7;">
        <strong>Total:</strong> Bs. {costo_fijo_total:,.2f}<br><br>
        {detalle_text_fijo}
    </div>
</div>
"""

responsive_grid([card_variables, card_fijos], min_col_width_px=300, gap="1rem")

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
    
    # Card de información del margen usando HTML directo
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    ">
        <h4 style="color: #60A5FA; margin-top: 0; display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.5rem;">💡</span>
            <span>Información del Margen</span>
        </h4>
        <div style="color: #E5E7EB; margin-top: 1rem; line-height: 1.7;">
            <strong>Margen Seleccionado:</strong> {margen_rate}%<br><br>
            El precio sugerido incluirá este margen sobre el costo total del lote.<br><br>
            <strong>Recomendaciones:</strong><br>
            • Bajo (0-10%): Competitivo<br>
            • Medio (10-20%): Equilibrado<br>
            • Alto (>20%): Premium
        </div>
    </div>
    """, unsafe_allow_html=True)

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
                
                # Métricas principales de predicción (responsive)
                st.markdown("### 📊 Resultados Principales")
                
                precio_compra = prediction.get("precio_compra_kg", 0)  # Precio de compra original
                precio_sugerido = prediction.get("precio_sugerido_kg", 0)  # Precio final con margen seleccionado
                precio_base_estimado = prediction.get("precio_base_estimado", 0)  # Precio base sin margen adicional
                precio_ml_base = prediction.get("precio_ml_base", precio_base_estimado)
                variable_por_kg = prediction.get("variable_por_kg", 0)  # Costos variables por kg (para info)
                fijo_por_kg = prediction.get("fijo_por_kg", 0)  # Costos fijos por kg (para info)
                margen_rate = prediction.get("margen_rate", 0.10)
                margen_valor_kg = prediction.get("margen_valor_kg", precio_base_estimado * margen_rate)
                subtotal = precio_base_estimado  # El precio base ya incluye costos (sin margen adicional)
                margen_aplicado = margen_rate * 100
                margen_formato = f"{margen_aplicado:.0f}%" if margen_aplicado % 1 == 0 else f"{margen_aplicado:.2f}%"
                ganancia_neta = prediction.get("ganancia_neta_estimada", 0)

                stats_card_responsive([
                    {"label": "Precio Compra", "value": f"{precio_compra:.2f}", "icon": "🛒", "color": "info"},
                    {"label": "Variables por kg", "value": f"{variable_por_kg:.2f}", "icon": "📈", "color": "warning"},
                    {"label": "Fijos por kg", "value": f"{fijo_por_kg:.2f}", "icon": "🏢", "color": "info"},
                    {"label": "Precio Sugerido (ML)", "value": f"{precio_sugerido:.2f}", "icon": "🤖", "color": "primary", "delta": "Predicción ML", "delta_color": "positive"},
                    {"label": "Ganancia Neta", "value": f"{ganancia_neta:,.2f}", "icon": "💵", "color": "success"},
                ], min_col_width_px=220, gap="1rem")
                
                st.markdown("### Desglose Detallado")
                st.divider()
                
                # Tabla de desglose
                st.markdown("### 📋 Desglose de Cálculo")
                
                desglose_data = {
                    "Concepto": [
                        "Precio Compra",
                        "Costos Variables por kg",
                        "Costos Fijos por kg",
                        "Precio Base Estimado",
                        f"Margen ({margen_rate*100:.0f}%)",
                        "Precio Sugerido (ML)"
                    ],
                    "Valor (Bs/kg)": [
                        f"{precio_compra:.2f}",
                        f"{variable_por_kg:.2f}",
                        f"{fijo_por_kg:.2f}",
                        f"{precio_base_estimado:.2f}",
                        f"{margen_valor_kg:.2f}",
                        f"{precio_sugerido:.2f}"
                    ],
                    "Nota": [
                        "Input", "Feature ML", "Feature ML", "Estimado", "Estimado", "🤖 Predicción ML"
                    ]
                }
                
                df_desglose = pd.DataFrame(desglose_data)
                st.dataframe(df_desglose, use_container_width=True, hide_index=True)
                
                # Información adicional
                st.markdown("### 📊 Información del Modelo y Análisis Avanzado")
                st.divider()
                
                # Obtener información del modelo desde la respuesta
                modelo_info = prediction.get("modelo", {})
                desglose_indirectos = prediction.get("desglose_costos_indirectos", {})
                estacionalidad = prediction.get("estacionalidad", {})
                
                # Cards de información adicional (responsive)
                card_modelo = f"""
                <div style="background: linear-gradient(135deg, rgba(255, 145, 164, 0.1) 0%, rgba(255, 127, 149, 0.1) 100%); border: 1px solid rgba(255, 145, 164, 0.3); border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem;">
                    <h4 style="color: #FF91A4; margin-top: 0; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.5rem;">🤖</span>
                        <span>Información del Modelo</span>
                    </h4>
                    <div style="color: #E5E7EB; margin-top: 1rem; line-height: 1.7;">
                        <strong>Modelo:</strong> {modelo_info.get('nombre', 'XGBoost v1.0')}<br>
                        <strong>MAE (Error Promedio):</strong> {modelo_info.get('mae', 0):.4f} Bs/kg<br>
                        <strong>R² (Precisión):</strong> {modelo_info.get('r2', 0):.4f} ({modelo_info.get('r2', 0)*100:.1f}%)<br>
                        <strong>Features Utilizadas:</strong> {modelo_info.get('n_features', 24)}<br>
                        <small style="color: #9CA3AF;">El modelo se equivoca en promedio por {modelo_info.get('mae', 0):.2f} Bs/kg</small>
                    </div>
                </div>
                """
                
                # Card de desglose de costos indirectos
                card_indirectos = f"""
                <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem;">
                    <h4 style="color: #60A5FA; margin-top: 0; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.5rem;">💡</span>
                        <span>Desglose de Costos Indirectos</span>
                    </h4>
                    <div style="color: #E5E7EB; margin-top: 1rem; line-height: 1.7;">
                        <strong>Energía y Agua (Prorrateado):</strong> Bs. {desglose_indirectos.get('tasa_consumo_energia_agua', 0):.2f}<br>
                        <strong>Mano de Obra (Prorrateado):</strong> Bs. {desglose_indirectos.get('costo_mano_obra_asignada', 0):.2f}<br>
                        <strong>Costo Fijo Diario:</strong> Bs. {desglose_indirectos.get('costo_fijo_diario_lote', 0):.2f}<br>
                        <strong>Factor de Ocupación:</strong> {desglose_indirectos.get('factor_ocupacion_granja', 0):.2%}<br>
                        <small style="color: #9CA3AF;">Costos prorrateados según animales vendidos en el mes</small>
                    </div>
                </div>
                """
                
                # Card de estacionalidad
                mensaje_estacionalidad = estacionalidad.get('mensaje', 'Sin festividades próximas')
                color_estacionalidad = "#10B981" if estacionalidad.get('es_feriado_proximo') else "#6B7280"
                icon_estacionalidad = "🎉" if estacionalidad.get('es_feriado_proximo') else "📅"
                
                card_estacionalidad = f"""
                <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem;">
                    <h4 style="color: {color_estacionalidad}; margin-top: 0; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.5rem;">{icon_estacionalidad}</span>
                        <span>Análisis de Estacionalidad</span>
                    </h4>
                    <div style="color: #E5E7EB; margin-top: 1rem; line-height: 1.7;">
                        <strong>Mes de Adquisición:</strong> {estacionalidad.get('mes_adquisicion', 'N/A')}<br>
                        <strong>Feriado Próximo:</strong> {'Sí' if estacionalidad.get('es_feriado_proximo') else 'No'}<br>
                        <strong>Días para Festividad:</strong> {estacionalidad.get('dias_para_festividad', 999)}<br><br>
                        <strong style="color: {color_estacionalidad};">{mensaje_estacionalidad}</strong>
                    </div>
                </div>
                """

                responsive_grid([card_modelo, card_indirectos, card_estacionalidad], min_col_width_px=300, gap="1rem")
                
                # Gráfico de comparación
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### 📈 Visualización Comparativa")
                
                df_comparacion = pd.DataFrame({
                    'Componente': ['Precio Compra', 'Variables/kg', 'Fijos/kg', 'Margen', 'Precio Final'],
                    'Valor': [
                        precio_compra,
                        variable_por_kg,
                        fijo_por_kg,
                        margen_valor_kg,
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
