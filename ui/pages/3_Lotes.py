"""
Gestión de Lotes - Versión Profesional
CRUD completo con diseño moderno y UX mejorada
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
from utils.professional_components import (
    modern_card, metric_card, badge, status_indicator,
    empty_state_modern, alert_modern, show_toast, skeleton_loader,
    stats_card_responsive
)
# Componentes de navegación removidos - usando Streamlit nativo
from utils.styles import inject_custom_css

# Configuración de página
from utils.simple_sidebar import page_config, render_simple_sidebar

page_config("Lotes - Sistema de Gestión", "🐷")

# Autenticación y estilos
require_auth()
inject_custom_css()
inject_reload_warning()

# Sidebar simple
user = get_current_user()
render_simple_sidebar("3_Lotes.py", user)

# Header de página
st.title("🐷 Gestión de Lotes")
st.caption("Administra tus lotes de cerdos: crear, editar y eliminar")
st.divider()

# API Client
api = APIClient()

# ==================== TABS PRINCIPALES ====================

tab1, tab2, tab3 = st.tabs(["📋 Listar Lotes", "➕ Crear Lote", "✏️ Editar Lote"])

# ==================== TAB 1: LISTAR LOTES ====================

with tab1:
    # Limpiar estado del lote creado cuando se cambia a esta pestaña
    if "lote_creado_data" in st.session_state:
        del st.session_state["lote_creado_data"]
    if "mostrar_lote_creado" in st.session_state:
        del st.session_state["mostrar_lote_creado"]
    st.markdown("### 📊 Lista de Lotes Registrados")
    
    col_actions = st.columns([2, 1, 1])
    
    with col_actions[0]:
        search_term = st.text_input("🔍 Buscar por número de lote...", key="lote_search", placeholder="Buscar por número de lote...")
    
    with col_actions[1]:
        sort_option = st.selectbox(
            "Ordenar por",
            ["Número (Descendente)", "Número (Ascendente)", "Fecha (Reciente)", "Fecha (Antigua)"],
            key="sort_lotes"
        )
    
    with col_actions[2]:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Actualizar", use_container_width=True):
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.spinner("Cargando lotes..."):
        result = api.get_lotes()
        
        if result["success"]:
            lotes = result["data"]
            
            if lotes:
                # Filtrar por búsqueda
                filtered_lotes = lotes
                if search_term:
                    try:
                        search_id = int(search_term)
                        filtered_lotes = [l for l in filtered_lotes if l.get("id_lote") == search_id]
                    except ValueError:
                        filtered_lotes = []
                        alert_modern("El número debe ser válido", "warning")
                
                # Ordenar
                if sort_option == "Número (Descendente)":
                    filtered_lotes = sorted(filtered_lotes, key=lambda x: x.get("id_lote", 0), reverse=True)
                elif sort_option == "Número (Ascendente)":
                    filtered_lotes = sorted(filtered_lotes, key=lambda x: x.get("id_lote", 0))
                elif sort_option == "Fecha (Reciente)":
                    filtered_lotes = sorted(filtered_lotes, key=lambda x: x.get("fecha_adquisicion", ""), reverse=True)
                elif sort_option == "Fecha (Antigua)":
                    filtered_lotes = sorted(filtered_lotes, key=lambda x: x.get("fecha_adquisicion", ""))
                
                # Mostrar métricas rápidas (responsive)
                total_animales = sum(l.get("cantidad_animales", 0) for l in filtered_lotes)
                peso_prom = sum(l.get("peso_promedio_entrada", 0) for l in filtered_lotes) / len(filtered_lotes) if filtered_lotes else 0
                precio_prom = sum(l.get("precio_compra_kg", 0) or 0 for l in filtered_lotes) / len([l for l in filtered_lotes if l.get("precio_compra_kg")]) if filtered_lotes else 0

                stats_card_responsive([
                    {"label": "Total Lotes", "value": len(filtered_lotes), "icon": "🐷", "color": "primary"},
                    {"label": "Total Animales", "value": f"{total_animales:,}", "icon": "🐖", "color": "success"},
                    {"label": "Peso Promedio", "value": f"{peso_prom:.2f} kg", "icon": "⚖️", "color": "warning"},
                    {"label": "Precio Promedio", "value": f"{precio_prom:.2f} Bs/kg", "icon": "💰", "color": "info"},
                ], min_col_width_px=260, gap="1rem")
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.divider()
                
                # Tabla de datos
                if filtered_lotes:
                    st.markdown(f"**Mostrando {len(filtered_lotes)} lote(s)**")
                    
                    df_data = []
                    for lote in filtered_lotes:
                        fecha = lote.get("fecha_adquisicion", "N/A")
                        if fecha and fecha != "N/A":
                            # Remover hora si existe
                            if isinstance(fecha, str):
                                if "T" in fecha:
                                    fecha = fecha.split("T")[0]
                                elif " " in fecha:
                                    fecha = fecha.split(" ")[0]
                                try:
                                    fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
                                    fecha = fecha_obj.strftime("%d/%m/%Y")
                                except:
                                    pass
                            elif isinstance(fecha, datetime):
                                fecha = fecha.strftime("%d/%m/%Y")
                        
                        df_data.append({
                            "Número del Lote": lote.get("id_lote", "N/A"),
                            "Fecha Adquisición": fecha,
                            "Cantidad Animales": lote.get("cantidad_animales", 0),
                            "Peso Prom. (kg)": f"{lote.get('peso_promedio_entrada', 0):.2f}",
                            "Precio (Bs/kg)": f"{lote.get('precio_compra_kg', 0) or 0:.2f}",
                            "Duración (días)": lote.get("duracion_estadia_dias", 0) or 0,
                        })
                    
                    df = pd.DataFrame(df_data)
                    
                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True,
                        height=500
                    )
                else:
                    empty_state_modern(
                        icon="🔍",
                        title="No se encontraron lotes",
                        description="Intenta con otros criterios de búsqueda o crea un nuevo lote."
                    )
            else:
                empty_state_modern(
                    icon="🐷",
                    title="No hay lotes registrados",
                    description="Crea tu primer lote para comenzar a gestionar tu producción.",
                    action_label="Crear Primer Lote",
                    action_callback=lambda: st.session_state.update({"active_tab": 1})
                )
        else:
            alert_modern(
                message=f"Error al cargar lotes: {result.get('error', 'Error desconocido')}",
                type="error",
                title="Error de Conexión"
            )

# ==================== TAB 2: CREAR LOTE ====================

with tab2:
    # Limpiar estado del lote creado si el usuario cambia de pestaña
    # Solo mantenerlo si acabamos de crear un lote (mostrar_lote_creado está activo)
    if "lote_creado_data" in st.session_state:
        # Verificar si tenemos la flag de mostrar activa
        if not st.session_state.get("mostrar_lote_creado", False):
            # Limpiar el estado si no está activo
            if "lote_creado_data" in st.session_state:
                del st.session_state["lote_creado_data"]
    
    st.markdown("### ➕ Crear Nuevo Lote")
    st.markdown("Completa el formulario para registrar un nuevo lote en el sistema")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Mostrar detalles del lote creado si existe en el estado
    if "lote_creado_data" in st.session_state and st.session_state.get("mostrar_lote_creado", False):
        lote_creado = st.session_state["lote_creado_data"]
        lote_id = lote_creado.get('id_lote', 'N/A')
        
        alert_modern(
            message=f"Lote creado exitosamente. Número del Lote: {lote_id}",
            type="success",
            title="¡Éxito!"
        )
        
        # Mostrar datos del lote creado de forma amigable
        st.markdown("### 📋 Detalles del Lote Creado")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Cards con la información principal (responsive)
        peso = lote_creado.get('peso_promedio_entrada', 0)
        precio = lote_creado.get('precio_compra_kg', 0) or 0
        stats_card_responsive([
            {"label": "Número del Lote", "value": lote_id, "icon": "🔢", "color": "primary"},
            {"label": "Cantidad de Animales", "value": lote_creado.get('cantidad_animales', 0), "icon": "🐖", "color": "success"},
                    {"label": "Peso Promedio", "value": f"{peso:.2f} kg", "icon": "⚖️", "color": "warning"},
                    {"label": "Precio Compra", "value": f"Bs. {precio:.2f}/kg" if precio > 0 else "No especificado", "icon": "💰", "color": "info"},
        ], min_col_width_px=260, gap="1rem")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Botón para crear otro lote y limpiar el formulario
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("➕ Crear Otro Lote", use_container_width=True, type="primary"):
                # Limpiar el estado y refrescar
                if "lote_creado_data" in st.session_state:
                    del st.session_state["lote_creado_data"]
                if "mostrar_lote_creado" in st.session_state:
                    del st.session_state["mostrar_lote_creado"]
                st.rerun()
        
        st.markdown("---")
        st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("create_lote_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📅 Información Básica")
            fecha_adquisicion = st.date_input(
                "Fecha de Adquisición *",
                value=datetime.now().date(),
                help="Fecha en que se adquirió el lote"
            )
            
            cantidad_animales = st.number_input(
                "Cantidad de Animales *",
                min_value=1,
                value=10,
                step=1,
                help="Número total de animales en el lote"
            )
            
            peso_promedio_entrada = st.number_input(
                "Peso Promedio de Entrada (kg) *",
                min_value=0.1,
                value=20.0,
                step=0.1,
                help="Peso promedio de los animales al momento de adquisición"
            )
        
        with col2:
            st.markdown("#### 💰 Información Comercial")
            precio_compra_kg = st.number_input(
                "Precio de Compra (Bs/kg)",
                min_value=0.0,
                value=0.0,
                step=0.01,
                help="Precio de compra por kilogramo (opcional)"
            )
            
            duracion_estadia_dias = st.number_input(
                "Duración de Estadía (días)",
                min_value=0,
                max_value=7,
                value=0,
                step=1,
                help="Tiempo de permanencia en días (máximo 7 días)"
            )
            
            st.info("💡 **Tip:** Los campos marcados con * son obligatorios")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_submit1, col_submit2, col_submit3 = st.columns([1, 2, 1])
        
        with col_submit2:
            submit = st.form_submit_button(
                "✅ Crear Lote",
                use_container_width=True,
                type="primary"
            )
        
        if submit:
            # Validaciones
            if cantidad_animales <= 0:
                alert_modern("La cantidad de animales debe ser mayor a 0", "error")
            elif peso_promedio_entrada <= 0:
                alert_modern("El peso promedio debe ser mayor a 0", "error")
            else:
                lote_data = {
                    "fecha_adquisicion": fecha_adquisicion.isoformat(),
                    "cantidad_animales": int(cantidad_animales),
                    "peso_promedio_entrada": float(peso_promedio_entrada),
                    "duracion_estadia_dias": int(duracion_estadia_dias) if duracion_estadia_dias else None,
                    "precio_compra_kg": float(precio_compra_kg) if precio_compra_kg > 0 else None,
                }
                
                with st.spinner("Creando lote..."):
                    result = api.create_lote(lote_data)
                    
                    if result["success"]:
                        lote_creado = result["data"]
                        
                        # Guardar el lote creado en el estado de sesión para mostrarlo después
                        st.session_state["lote_creado_data"] = lote_creado
                        st.session_state["mostrar_lote_creado"] = True
                        
                        st.balloons()
                        st.rerun()  # Refrescar para mostrar los detalles
                    else:
                        alert_modern(
                            message=f"Error al crear lote: {result.get('error', 'Error desconocido')}",
                            type="error",
                            title="Error"
                        )

# ==================== TAB 3: EDITAR LOTE ====================

with tab3:
    # Limpiar estado del lote creado cuando se cambia a esta pestaña
    if "lote_creado_data" in st.session_state:
        del st.session_state["lote_creado_data"]
    if "mostrar_lote_creado" in st.session_state:
        del st.session_state["mostrar_lote_creado"]
    st.markdown("### ✏️ Editar Lote Existente")
    st.markdown("Selecciona un lote para modificar o eliminar")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.spinner("Cargando lotes..."):
        result = api.get_lotes()
        
        if result["success"]:
            lotes = result["data"]
            
            if lotes:
                # Crear opciones de selección más descriptivas
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
                    
                    label = f"Número: {l['id_lote']} | {l.get('cantidad_animales', 0)} animales | {fecha}"
                    lote_options[label] = l['id_lote']
                
                selected_lote_str = st.selectbox(
                    "Selecciona un lote para editar",
                    options=list(lote_options.keys()),
                    key="edit_lote_selector"
                )
                
                selected_lote_id = lote_options[selected_lote_str]
                selected_lote = next((l for l in lotes if l['id_lote'] == selected_lote_id), None)
                
                if selected_lote:
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Mostrar información actual del lote con cards modernas (responsive)
                    st.markdown("### 📊 Información Actual del Lote")
                    peso = selected_lote.get('peso_promedio_entrada', 0)
                    precio = selected_lote.get('precio_compra_kg', 0) or 0
                    stats_card_responsive([
                        {"label": "Número del Lote", "value": selected_lote_id, "icon": "🔢", "color": "primary"},
                        {"label": "Animales", "value": selected_lote.get('cantidad_animales', 0), "icon": "🐖", "color": "success"},
                        {"label": "Peso Promedio", "value": f"{peso:.2f} kg", "icon": "⚖️", "color": "warning"},
                        {"label": "Precio Compra", "value": f"Bs. {precio:.2f}/kg" if precio > 0 else "No especificado", "icon": "💰", "color": "info"},
                    ], min_col_width_px=260, gap="1rem")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    with st.form("edit_lote_form"):
                        st.markdown(f"**Editando Lote Número: {selected_lote_id}**")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Preparar fecha actual
                            fecha_actual = selected_lote.get("fecha_adquisicion", datetime.now().isoformat())
                            if fecha_actual and "T" in fecha_actual:
                                fecha_actual = fecha_actual.split("T")[0]
                            try:
                                fecha_obj = datetime.strptime(fecha_actual, "%Y-%m-%d").date()
                            except:
                                fecha_obj = datetime.now().date()
                            
                            fecha_adquisicion = st.date_input("Fecha de Adquisición", value=fecha_obj)
                            cantidad_animales = st.number_input(
                                "Cantidad de Animales",
                                min_value=1,
                                value=selected_lote.get("cantidad_animales", 10),
                                step=1
                            )
                            peso_promedio_entrada = st.number_input(
                                "Peso Promedio de Entrada (kg)",
                                min_value=0.1,
                                value=float(selected_lote.get("peso_promedio_entrada", 20.0)),
                                step=0.1
                            )
                        
                        with col2:
                            precio_actual = selected_lote.get("precio_compra_kg") or 0.0
                            precio_compra_kg = st.number_input(
                                "Precio de Compra (Bs/kg)",
                                min_value=0.0,
                                value=float(precio_actual),
                                step=0.01
                            )
                            
                            duracion_actual = selected_lote.get("duracion_estadia_dias") or 0
                            duracion_estadia_dias = st.number_input(
                                "Duración de Estadía (días)",
                                min_value=0,
                                max_value=7,
                                value=int(duracion_actual),
                                step=1
                            )
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        col_btn1, col_btn2 = st.columns(2)
                        
                        with col_btn1:
                            update_submit = st.form_submit_button(
                                "💾 Actualizar Lote",
                                use_container_width=True,
                                type="primary"
                            )
                        
                        with col_btn2:
                            delete_clicked = st.form_submit_button(
                                "🗑️ Eliminar Lote",
                                use_container_width=True,
                                type="secondary"
                            )
                        
                        if update_submit:
                            lote_data = {
                                "fecha_adquisicion": fecha_adquisicion.isoformat(),
                                "cantidad_animales": int(cantidad_animales),
                                "peso_promedio_entrada": float(peso_promedio_entrada),
                                "duracion_estadia_dias": int(duracion_estadia_dias) if duracion_estadia_dias else None,
                                "precio_compra_kg": float(precio_compra_kg) if precio_compra_kg > 0 else None,
                            }
                            
                            with st.spinner("Actualizando lote..."):
                                result = api.update_lote(selected_lote_id, lote_data)
                                
                                if result["success"]:
                                    alert_modern(
                                        message=f"Lote Número {selected_lote_id} actualizado correctamente",
                                        type="success",
                                        title="¡Actualización Exitosa!"
                                    )
                                    st.balloons()
                                    st.rerun()
                                else:
                                    alert_modern(
                                        message=f"Error: {result.get('error', 'Error desconocido')}",
                                        type="error",
                                        title="Error al Actualizar"
                                    )
                        
                        if delete_clicked:
                            st.warning("⚠️ ¿Estás seguro de que deseas eliminar este lote? Esta acción no se puede deshacer.")
                            
                            col_confirm1, col_confirm2 = st.columns(2)
                            
                            with col_confirm1:
                                if st.button("❌ Cancelar", use_container_width=True):
                                    st.info("Operación cancelada")
                            
                            with col_confirm2:
                                if st.button("✅ Confirmar Eliminación", use_container_width=True, type="primary"):
                                    with st.spinner("Eliminando lote..."):
                                        result = api.delete_lote(selected_lote_id)
                                        
                                        if result["success"]:
                                            alert_modern(
                                                message=f"Lote Número {selected_lote_id} eliminado correctamente",
                                                type="success",
                                                title="¡Eliminación Exitosa!"
                                            )
                                            st.rerun()
                                        else:
                                            alert_modern(
                                                message=f"Error: {result.get('error', 'Error desconocido')}",
                                                type="error",
                                                title="Error al Eliminar"
                                            )
            else:
                empty_state_modern(
                    icon="🐷",
                    title="No hay lotes para editar",
                    description="Crea un lote primero en la pestaña 'Crear Lote'."
                )
        else:
            alert_modern(
                message=f"Error al cargar lotes: {result.get('error', 'Error desconocido')}",
                type="error",
                title="Error de Conexión"
            )
