"""
Componentes Profesionales UI/UX
Sistema de componentes modernos tipo SaaS con las mejores prácticas de diseño
"""
import streamlit as st
from typing import Optional, Dict, Any, List, Literal
import pandas as pd
from datetime import datetime
import time


# ==================== CARDS Y CONTAINERS ====================

def modern_card(
    title: Optional[str] = None,
    content: str = "",
    icon: Optional[str] = None,
    color: str = "default",
    padding: str = "default"
):
    """
    Card moderno con estilo profesional para tema oscuro
    
    Args:
        title: Título del card
        content: Contenido del card
        icon: Emoji o icono
        color: Color del card (default, primary, success, warning, error, info)
        padding: Tamaño del padding (small, default, large)
    """
    color_map = {
        "default": "linear-gradient(135deg, #0A0A0A 0%, #1A1A2E 100%)",
        "primary": "linear-gradient(135deg, #1A0A0F 0%, #2A1A1F 100%)",
        "success": "linear-gradient(135deg, #0A1A10 0%, #1A2A1F 100%)",
        "warning": "linear-gradient(135deg, #1A150A 0%, #2A251A 100%)",
        "error": "linear-gradient(135deg, #1A0A0A 0%, #2A1A1A 100%)",
        "info": "linear-gradient(135deg, #0A0F1A 0%, #1A1F2A 100%)"
    }
    
    border_color_map = {
        "default": "#3A3A4A",
        "primary": "#4A2A35",
        "success": "#2A4A35",
        "warning": "#4A3A2A",
        "error": "#4A2A2A",
        "info": "#2A354A"
    }
    
    padding_map = {
        "small": "1rem",
        "default": "1.5rem",
        "large": "2rem"
    }
    
    bg_color = color_map.get(color, color_map["default"])
    border = border_color_map.get(color, border_color_map["default"])
    pad = padding_map.get(padding, padding_map["default"])
    
    icon_html = f'<span style="font-size: 1.75rem; margin-right: 0.75rem;">{icon}</span>' if icon else ''
    title_html = f'<h3 style="margin: 0 0 1rem 0; font-size: 1.125rem; font-weight: 600; color: #FFFFFF; display: flex; align-items: center;">{icon_html}{title}</h3>' if title else ''
    
    st.markdown(f"""
    <div style="
        background: {bg_color};
        border: 2px solid {border};
        border-radius: 16px;
        padding: {pad};
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 25px rgba(255, 145, 164, 0.2)'; this.style.borderColor='#FF91A4';" 
       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(0, 0, 0, 0.3)'; this.style.borderColor='{border}';">
        {title_html}
        <div style="color: #E0E0E0; line-height: 1.7; font-size: 0.9375rem;">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)


def metric_card(
    label: str,
    value: Any,
    icon: str = "📊",
    delta: Optional[str] = None,
    delta_color: str = "positive",
    trend_data: Optional[List[float]] = None,
    color: str = "primary"
):
    """
    Card de métrica profesional con indicadores visuales
    
    Args:
        label: Etiqueta de la métrica
        value: Valor de la métrica
        icon: Icono/emoji
        delta: Cambio o delta
        delta_color: Color del delta (positive, negative, neutral)
        trend_data: Datos para mini gráfico de tendencia
        color: Color del card
    """
    color_schemes = {
        "primary": {"main": "#3B82F6", "light": "#DBEAFE", "bg": "#EFF6FF"},
        "success": {"main": "#10B981", "light": "#D1FAE5", "bg": "#ECFDF5"},
        "warning": {"main": "#F59E0B", "light": "#FDE68A", "bg": "#FFFBEB"},
        "error": {"main": "#EF4444", "light": "#FECACA", "bg": "#FEF2F2"},
        "info": {"main": "#06B6D4", "light": "#A5F3FC", "bg": "#ECFEFF"},
    }
    
    scheme = color_schemes.get(color, color_schemes["primary"])
    
    delta_html = ""
    if delta:
        delta_colors = {
            "positive": "#10B981",
            "negative": "#EF4444",
            "neutral": "#6B7280"
        }
        delta_color_val = delta_colors.get(delta_color, delta_colors["neutral"])
        delta_icon = "↗" if delta_color == "positive" else "↘" if delta_color == "negative" else "→"
        delta_html = f"""
        <div style="
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            font-size: 0.875rem;
            color: {delta_color_val};
            font-weight: 600;
            margin-top: 0.5rem;
        ">
            <span>{delta_icon}</span>
            <span>{delta}</span>
        </div>
        """
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #0A0A0A 0%, #1A1A2E 100%);
        border: 2px solid #3A3A4A;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        height: 100%;
        position: relative;
        overflow: hidden;
    " onmouseover="this.style.transform='translateY(-6px)'; this.style.boxShadow='0 12px 40px rgba(255, 145, 164, 0.25)'; this.style.borderColor='#FF91A4';" 
       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(0, 0, 0, 0.3)'; this.style.borderColor='#3A3A4A';">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
            <div style="
                background: rgba(255, 145, 164, 0.1);
                border: 2px solid rgba(255, 145, 164, 0.2);
                border-radius: 12px;
                padding: 0.75rem;
                font-size: 1.75rem;
                transition: all 0.3s ease;
            ">
                {icon}
            </div>
            <div style="flex: 1;">
                <div style="color: #B0B0B0; font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.5px;">
                    {label}
                </div>
                <div style="color: #FFFFFF; font-size: 2rem; font-weight: 700; line-height: 1; background: linear-gradient(135deg, #FFFFFF 0%, #E0E0E0 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                    {value}
                </div>
            </div>
        </div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def stats_card_row(stats: List[Dict[str, Any]]):
    """
    Fila de cards de estadísticas
    
    Args:
        stats: Lista de diccionarios con label, value, icon, delta, color
    """
    cols = st.columns(len(stats))
    for col, stat in zip(cols, stats):
        with col:
            metric_card(
                label=stat.get("label", ""),
                value=stat.get("value", ""),
                icon=stat.get("icon", "📊"),
                delta=stat.get("delta"),
                delta_color=stat.get("delta_color", "neutral"),
                color=stat.get("color", "primary")
            )


# ==================== MODALS Y DIALOGS ====================

def confirmation_dialog(
    message: str,
    confirm_label: str = "Confirmar",
    cancel_label: str = "Cancelar",
    type: str = "warning"
) -> bool:
    """
    Dialog de confirmación profesional
    
    Args:
        message: Mensaje a mostrar
        confirm_label: Texto del botón de confirmación
        cancel_label: Texto del botón de cancelar
        type: Tipo de dialog (warning, error, info)
    
    Returns:
        True si se confirmó, False si se canceló
    """
    icons = {
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️",
        "success": "✅"
    }
    
    icon = icons.get(type, icons["warning"])
    
    st.markdown(f"""
    <div style="
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        border: 2px solid #F3F4F6;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    ">
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">{icon}</div>
            <div style="font-size: 1.125rem; color: #1F2937; font-weight: 500;">
                {message}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(cancel_label, key="cancel_dialog", use_container_width=True):
            return False
    with col2:
        if st.button(confirm_label, key="confirm_dialog", type="primary", use_container_width=True):
            return True
    return False


# ==================== BADGES Y TAGS ====================

def badge(text: str, color: str = "default", size: str = "default"):
    """
    Badge moderno con múltiples estilos
    
    Args:
        text: Texto del badge
        color: Color (default, primary, success, warning, error, info)
        size: Tamaño (small, default, large)
    """
    color_schemes = {
        "default": {"bg": "#F3F4F6", "text": "#374151"},
        "primary": {"bg": "#DBEAFE", "text": "#1E40AF"},
        "success": {"bg": "#D1FAE5", "text": "#065F46"},
        "warning": {"bg": "#FEF3C7", "text": "#92400E"},
        "error": {"bg": "#FEE2E2", "text": "#991B1B"},
        "info": {"bg": "#E0E7FF", "text": "#3730A3"},
    }
    
    size_map = {
        "small": {"font": "0.75rem", "padding": "0.25rem 0.625rem"},
        "default": {"font": "0.875rem", "padding": "0.375rem 0.875rem"},
        "large": {"font": "1rem", "padding": "0.5rem 1rem"}
    }
    
    scheme = color_schemes.get(color, color_schemes["default"])
    sizing = size_map.get(size, size_map["default"])
    
    st.markdown(f"""
    <span style="
        display: inline-flex;
        align-items: center;
        background: {scheme['bg']};
        color: {scheme['text']};
        font-size: {sizing['font']};
        font-weight: 600;
        padding: {sizing['padding']};
        border-radius: 9999px;
        margin-right: 0.5rem;
    ">
        {text}
    </span>
    """, unsafe_allow_html=True)


def status_indicator(status: str, text: str = ""):
    """
    Indicador de estado con punto de color
    
    Args:
        status: Estado (active, inactive, pending, success, error)
        text: Texto adicional
    """
    status_colors = {
        "active": "#10B981",
        "inactive": "#6B7280",
        "pending": "#F59E0B",
        "success": "#10B981",
        "error": "#EF4444",
        "warning": "#F59E0B"
    }
    
    color = status_colors.get(status, status_colors["inactive"])
    display_text = text or status.capitalize()
    
    st.markdown(f"""
    <div style="
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.875rem;
        color: #374151;
    ">
        <span style="
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: {color};
            box-shadow: 0 0 0 3px {color}33;
        "></span>
        <span style="font-weight: 500;">{display_text}</span>
    </div>
    """, unsafe_allow_html=True)


# ==================== NOTIFICACIONES TOAST ====================

def show_toast(
    message: str,
    type: str = "info",
    duration: int = 3000,
    position: str = "top-right"
):
    """
    Notificación toast profesional
    
    Args:
        message: Mensaje a mostrar
        type: Tipo (success, error, warning, info)
        duration: Duración en milisegundos
        position: Posición (top-right, top-left, bottom-right, bottom-left)
    """
    type_config = {
        "success": {"icon": "✓", "color": "#10B981", "bg": "#D1FAE5"},
        "error": {"icon": "✕", "color": "#EF4444", "bg": "#FEE2E2"},
        "warning": {"icon": "⚠", "color": "#F59E0B", "bg": "#FEF3C7"},
        "info": {"icon": "ℹ", "color": "#3B82F6", "bg": "#DBEAFE"}
    }
    
    config = type_config.get(type, type_config["info"])
    
    positions = {
        "top-right": "top: 1rem; right: 1rem;",
        "top-left": "top: 1rem; left: 1rem;",
        "bottom-right": "bottom: 1rem; right: 1rem;",
        "bottom-left": "bottom: 1rem; left: 1rem;"
    }
    
    pos = positions.get(position, positions["top-right"])
    
    st.markdown(f"""
    <div id="toast-notification" style="
        position: fixed;
        {pos}
        z-index: 9999;
        background: white;
        border-left: 4px solid {config['color']};
        border-radius: 8px;
        padding: 1rem 1.5rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        gap: 1rem;
        min-width: 300px;
        animation: slideIn 0.3s ease-out;
    ">
        <div style="
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: {config['bg']};
            color: {config['color']};
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.125rem;
        ">
            {config['icon']}
        </div>
        <div style="flex: 1; color: #1F2937; font-weight: 500;">
            {message}
        </div>
    </div>
    
    <style>
    @keyframes slideIn {{
        from {{
            transform: translateX(100%);
            opacity: 0;
        }}
        to {{
            transform: translateX(0);
            opacity: 1;
        }}
    }}
    </style>
    
    <script>
    setTimeout(function() {{
        var toast = document.getElementById('toast-notification');
        if (toast) {{
            toast.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(function() {{ toast.remove(); }}, 300);
        }}
    }}, {duration});
    </script>
    """, unsafe_allow_html=True)


# ==================== SKELETON LOADERS ====================

def skeleton_loader(type: str = "card", count: int = 1):
    """
    Skeleton loader profesional para estados de carga
    
    Args:
        type: Tipo de skeleton (card, table, text, metric)
        count: Número de skeletons a mostrar
    """
    skeleton_css = """
    <style>
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    .skeleton {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 1000px 100%;
        animation: shimmer 2s infinite;
        border-radius: 8px;
    }
    </style>
    """
    
    skeletons = {
        "card": """
        <div class="skeleton" style="height: 120px; margin-bottom: 1rem;"></div>
        """,
        "metric": """
        <div style="margin-bottom: 1rem;">
            <div class="skeleton" style="height: 20px; width: 60%; margin-bottom: 0.5rem;"></div>
            <div class="skeleton" style="height: 40px; width: 80%;"></div>
        </div>
        """,
        "table": """
        <div style="margin-bottom: 1rem;">
            <div class="skeleton" style="height: 40px; margin-bottom: 0.5rem;"></div>
            <div class="skeleton" style="height: 60px; margin-bottom: 0.5rem;"></div>
            <div class="skeleton" style="height: 60px; margin-bottom: 0.5rem;"></div>
            <div class="skeleton" style="height: 60px;"></div>
        </div>
        """,
        "text": """
        <div style="margin-bottom: 1rem;">
            <div class="skeleton" style="height: 20px; width: 100%; margin-bottom: 0.5rem;"></div>
            <div class="skeleton" style="height: 20px; width: 95%; margin-bottom: 0.5rem;"></div>
            <div class="skeleton" style="height: 20px; width: 90%;"></div>
        </div>
        """
    }
    
    skeleton_html = skeletons.get(type, skeletons["card"])
    
    html = skeleton_css
    for _ in range(count):
        html += skeleton_html
    
    st.markdown(html, unsafe_allow_html=True)


# ==================== TABLAS MODERNAS ====================

def modern_table(
    data: pd.DataFrame,
    selectable: bool = False,
    actions: Optional[List[Dict[str, Any]]] = None,
    highlight_row: Optional[int] = None,
    pagination: bool = True,
    rows_per_page: int = 10
):
    """
    Tabla moderna con estilo profesional
    
    Args:
        data: DataFrame con los datos
        selectable: Si permite selección de filas
        actions: Lista de acciones (botones) por fila
        highlight_row: Índice de fila a resaltar
        pagination: Activar paginación
        rows_per_page: Filas por página
    """
    if data.empty:
        st.info("📋 No hay datos para mostrar")
        return
    
    # Estilo mejorado para tablas
    st.markdown("""
    <style>
    .modern-table {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .modern-table table {
        width: 100%;
        border-collapse: collapse;
    }
    .modern-table th {
        background: #F9FAFB;
        color: #374151;
        font-weight: 600;
        font-size: 0.875rem;
        text-align: left;
        padding: 1rem;
        border-bottom: 2px solid #E5E7EB;
    }
    .modern-table td {
        padding: 1rem;
        border-bottom: 1px solid #F3F4F6;
        color: #1F2937;
        font-size: 0.875rem;
    }
    .modern-table tr:hover {
        background: #F9FAFB;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True,
        height=None if not pagination else rows_per_page * 45
    )


# ==================== PROGRESS Y FEEDBACK ====================

def progress_circle(
    value: float,
    max_value: float = 100,
    label: str = "",
    color: str = "primary",
    size: int = 120
):
    """
    Indicador de progreso circular
    
    Args:
        value: Valor actual
        max_value: Valor máximo
        label: Etiqueta
        color: Color
        size: Tamaño en píxeles
    """
    percentage = (value / max_value * 100) if max_value > 0 else 0
    
    color_map = {
        "primary": "#3B82F6",
        "success": "#10B981",
        "warning": "#F59E0B",
        "error": "#EF4444"
    }
    
    stroke_color = color_map.get(color, color_map["primary"])
    
    st.markdown(f"""
    <div style="text-align: center;">
        <svg width="{size}" height="{size}" viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="54" fill="none" stroke="#E5E7EB" stroke-width="8"/>
            <circle cx="60" cy="60" r="54" fill="none" stroke="{stroke_color}" stroke-width="8"
                    stroke-dasharray="{percentage * 3.39} 339"
                    stroke-linecap="round"
                    transform="rotate(-90 60 60)"
                    style="transition: stroke-dasharray 0.5s ease;"/>
            <text x="60" y="60" text-anchor="middle" dy="7" 
                  style="font-size: 24px; font-weight: 700; fill: #1F2937;">
                {percentage:.1f}%
            </text>
        </svg>
        {f'<div style="margin-top: 0.5rem; font-size: 0.875rem; color: #6B7280;">{label}</div>' if label else ''}
    </div>
    """, unsafe_allow_html=True)


def step_progress(current_step: int, total_steps: int, steps_labels: List[str]):
    """
    Indicador de progreso por pasos
    
    Args:
        current_step: Paso actual (1-indexed)
        total_steps: Total de pasos
        steps_labels: Etiquetas de cada paso
    """
    html = '<div style="display: flex; align-items: center; margin: 2rem 0;">'
    
    for i in range(1, total_steps + 1):
        # Estado del paso
        is_completed = i < current_step
        is_current = i == current_step
        
        # Color del paso
        if is_completed:
            color = "#10B981"
            icon = "✓"
        elif is_current:
            color = "#3B82F6"
            icon = str(i)
        else:
            color = "#E5E7EB"
            icon = str(i)
        
        text_color = "#FFFFFF" if (is_completed or is_current) else "#9CA3AF"
        
        # Círculo del paso
        html += f"""
        <div style="flex: 1; display: flex; flex-direction: column; align-items: center;">
            <div style="
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: {color};
                color: {text_color};
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 1rem;
                margin-bottom: 0.5rem;
            ">
                {icon}
            </div>
            <div style="font-size: 0.75rem; color: #6B7280; text-align: center;">
                {steps_labels[i-1] if i-1 < len(steps_labels) else f'Paso {i}'}
            </div>
        </div>
        """
        
        # Línea conectora
        if i < total_steps:
            line_color = "#10B981" if is_completed else "#E5E7EB"
            html += f"""
            <div style="
                flex: 1;
                height: 2px;
                background: {line_color};
                margin: 0 0.5rem 2rem 0.5rem;
            "></div>
            """
    
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ==================== EMPTY STATES ====================

def empty_state_modern(
    icon: str = "📭",
    title: str = "No hay datos",
    description: str = "",
    action_label: Optional[str] = None,
    action_callback: Optional[callable] = None
):
    """
    Estado vacío moderno y profesional para tema oscuro
    
    Args:
        icon: Emoji o icono
        title: Título
        description: Descripción
        action_label: Etiqueta del botón de acción
        action_callback: Función a ejecutar al hacer clic
    """
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, #0A0A0A 0%, #1A1A2E 100%);
        border-radius: 20px;
        border: 2px dashed #3A3A4A;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    ">
        <div style="font-size: 5rem; margin-bottom: 1.5rem; opacity: 0.7; filter: drop-shadow(0 4px 8px rgba(255, 145, 164, 0.2));">
            {icon}
        </div>
        <h3 style="font-size: 1.75rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.75rem; letter-spacing: -0.5px;">
            {title}
        </h3>
        {f'<p style="font-size: 1rem; color: #B0B0B0; margin-bottom: 2rem; line-height: 1.6;">{description}</p>' if description else ''}
    </div>
    """, unsafe_allow_html=True)
    
    if action_label and action_callback:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(action_label, type="primary", use_container_width=True):
                action_callback()


# ==================== ALERTS ====================

def alert_modern(
    message: str,
    type: str = "info",
    title: Optional[str] = None,
    dismissible: bool = False
):
    """
    Alerta moderna con múltiples estilos para tema oscuro
    
    Args:
        message: Mensaje de la alerta
        type: Tipo (info, success, warning, error)
        title: Título opcional
        dismissible: Si se puede cerrar
    """
    config = {
        "info": {"icon": "ℹ️", "color": "#3B82F6", "bg": "linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%)", "border": "rgba(59, 130, 246, 0.3)", "text": "#B5EAD7"},
        "success": {"icon": "✅", "color": "#10B981", "bg": "linear-gradient(135deg, rgba(168, 230, 207, 0.1) 0%, rgba(168, 230, 207, 0.05) 100%)", "border": "rgba(168, 230, 207, 0.3)", "text": "#A8E6CF"},
        "warning": {"icon": "⚠️", "color": "#F59E0B", "bg": "linear-gradient(135deg, rgba(255, 211, 165, 0.1) 0%, rgba(255, 211, 165, 0.05) 100%)", "border": "rgba(255, 211, 165, 0.3)", "text": "#FFD3A5"},
        "error": {"icon": "❌", "color": "#EF4444", "bg": "linear-gradient(135deg, rgba(255, 154, 162, 0.1) 0%, rgba(255, 154, 162, 0.05) 100%)", "border": "rgba(255, 154, 162, 0.3)", "text": "#FF9AA2"}
    }
    
    cfg = config.get(type, config["info"])
    title_html = f'<div style="font-weight: 600; margin-bottom: 0.5rem; font-size: 1rem; color: #FFFFFF;">{title}</div>' if title else ''
    
    st.markdown(f"""
    <div style="
        background: {cfg['bg']};
        border: 2px solid {cfg['border']};
        border-left: 4px solid {cfg['color']};
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin: 1.5rem 0;
        display: flex;
        align-items: start;
        gap: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    ">
        <div style="font-size: 1.75rem; line-height: 1; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">
            {cfg['icon']}
        </div>
        <div style="flex: 1; color: #E0E0E0;">
            {title_html}
            <div style="font-size: 0.9375rem; line-height: 1.6; color: {cfg['text']};">
                {message}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

