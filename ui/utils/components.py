"""
Componentes reutilizables para la aplicación Streamlit
Optimizados para móviles y siguiendo principios de UX/UI
"""
import streamlit as st
from typing import Optional, Dict, Any, List
import pandas as pd
from datetime import datetime


def metric_card(label: str, value: Any, delta: Optional[str] = None, help_text: Optional[str] = None):
    """
    Crea una tarjeta de métrica con estilo mejorado
    
    Args:
        label: Etiqueta de la métrica
        value: Valor de la métrica
        delta: Cambio o diferencia (opcional)
        help_text: Texto de ayuda (opcional)
    """
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.metric(
            label=label,
            value=value,
            delta=delta,
            help=help_text
        )
    
    return col1, col2


def loading_spinner(message: str = "Cargando..."):
    """Muestra un spinner de carga con mensaje"""
    return st.spinner(message)


def success_message(message: str):
    """Muestra un mensaje de éxito"""
    st.success(message)


def error_message(message: str, details: Optional[str] = None):
    """Muestra un mensaje de error con detalles opcionales"""
    st.error(message)
    if details:
        with st.expander("Ver detalles"):
            st.text(details)


def info_card(title: str, content: str):
    """Crea una tarjeta de información"""
    st.info(f"**{title}**\n\n{content}")


def warning_card(title: str, content: str):
    """Crea una tarjeta de advertencia"""
    st.warning(f"**{title}**\n\n{content}")


def empty_state(message: str, description: Optional[str] = None):
    """
    Muestra un estado vacío cuando no hay datos
    
    Args:
        message: Mensaje a mostrar
        description: Descripción adicional (opcional)
    """
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; color: #636E72;">
        <p style="font-size: 1.125rem; font-weight: 600; margin-bottom: 0.5rem;">{message}</p>
        {f'<p style="font-size: 0.875rem; color: #74C0FC;">{description}</p>' if description else ''}
    </div>
    """, unsafe_allow_html=True)


def data_table(data: List[Dict[str, Any]], key: Optional[str] = None, height: Optional[int] = None):
    """
    Crea una tabla de datos con estilo mejorado
    
    Args:
        data: Lista de diccionarios con los datos
        key: Clave única para la tabla
        height: Altura de la tabla (opcional)
    """
    if not data:
        return None
    
    df = pd.DataFrame(data)
    
    # Configurar altura si se proporciona
    if height:
        st.dataframe(
            df,
            width='stretch',
            hide_index=True,
            height=height
        )
    else:
        st.dataframe(
            df,
            width='stretch',
            hide_index=True
        )
    
    return df


def responsive_columns(num_columns: int, ratios: Optional[List[float]] = None):
    """
    Crea columnas responsivas que se adaptan a móviles
    En móviles, las columnas se apilan automáticamente gracias a CSS
    
    Args:
        num_columns: Número de columnas
        ratios: Proporciones de las columnas (opcional)
    
    Returns:
        Lista de columnas
    """
    # En Streamlit, las columnas se adaptan automáticamente
    # pero el CSS asegura que en móviles se apilen
    if ratios:
        return st.columns(ratios)
    else:
        # Para móviles, usar columnas con igual ancho
        # El CSS se encargará de apilarlas
        return st.columns(num_columns)


def mobile_friendly_button(label: str, key: Optional[str] = None, type: str = "primary", width: str = 'stretch'):
    """
    Crea un botón amigable para móviles
    
    Args:
        label: Etiqueta del botón
        key: Clave única
        type: Tipo de botón (primary, secondary)
        width: Ancho del botón ('stretch' para ancho completo, 'content' para ancho del contenido)
    """
    return st.button(
        label,
        key=key,
        type=type,
        width=width
    )


def mobile_friendly_input(label: str, value: str = "", placeholder: str = "", key: Optional[str] = None, help_text: Optional[str] = None):
    """
    Crea un input amigable para móviles
    
    Args:
        label: Etiqueta del input
        value: Valor por defecto
        placeholder: Texto de placeholder
        key: Clave única
        help_text: Texto de ayuda
    """
    return st.text_input(
        label,
        value=value,
        placeholder=placeholder,
        key=key,
        help=help_text
    )


def mobile_friendly_number_input(
    label: str,
    min_value: float = 0.0,
    max_value: Optional[float] = None,
    value: float = 0.0,
    step: float = 1.0,
    key: Optional[str] = None,
    help_text: Optional[str] = None
):
    """
    Crea un input numérico amigable para móviles
    
    Args:
        label: Etiqueta del input
        min_value: Valor mínimo
        max_value: Valor máximo (opcional)
        value: Valor por defecto
        step: Incremento
        key: Clave única
        help_text: Texto de ayuda
    """
    return st.number_input(
        label,
        min_value=min_value,
        max_value=max_value,
        value=value,
        step=step,
        key=key,
        help=help_text
    )


def mobile_friendly_selectbox(
    label: str,
    options: List[str],
    index: int = 0,
    key: Optional[str] = None,
    help_text: Optional[str] = None
):
    """
    Crea un selectbox amigable para móviles
    
    Args:
        label: Etiqueta del selectbox
        options: Lista de opciones
        index: Índice seleccionado por defecto
        key: Clave única
        help_text: Texto de ayuda
    """
    return st.selectbox(
        label,
        options=options,
        index=index,
        key=key,
        help=help_text
    )


def progress_bar(current: int, total: int, label: Optional[str] = None):
    """
    Muestra una barra de progreso
    
    Args:
        current: Valor actual
        total: Valor total
        label: Etiqueta (opcional)
    """
    progress = current / total if total > 0 else 0
    st.progress(progress)
    if label:
        st.caption(label)


def status_badge(status: str, color: str = "blue"):
    """
    Crea un badge de estado
    
    Args:
        status: Texto del estado
        color: Color del badge (blue, green, red, yellow)
    """
    color_map = {
        "blue": "#74C0FC",
        "green": "#51CF66",
        "red": "#FF6B6B",
        "yellow": "#FFD43B"
    }
    
    badge_color = color_map.get(color, color_map["blue"])
    
    st.markdown(f"""
    <span style="
        background-color: {badge_color};
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.875rem;
        font-weight: 600;
    ">{status}</span>
    """, unsafe_allow_html=True)


def divider():
    """Crea un divisor visual"""
    st.markdown("---")


def section_header(title: str, description: Optional[str] = None):
    """
    Crea un encabezado de sección con estilo
    
    Args:
        title: Título de la sección
        description: Descripción (opcional)
    """
    st.markdown(f"### {title}")
    if description:
        st.caption(description)
    divider()


def formatted_date(date_str: str) -> str:
    """
    Formatea una fecha ISO a formato legible (solo fecha, sin hora)
    
    Args:
        date_str: Fecha en formato ISO o datetime
    
    Returns:
        Fecha formateada en formato DD/MM/YYYY
    """
    if not date_str or date_str == "N/A":
        return "N/A"
    
    try:
        # Si es un objeto datetime, convertir directamente
        if isinstance(date_str, datetime):
            return date_str.strftime("%d/%m/%Y")
        
        # Si es string, intentar parsear
        if isinstance(date_str, str):
            # Remover hora si existe
            if "T" in date_str:
                date_str = date_str.split("T")[0]
            # Remover hora si está en formato "YYYY-MM-DD HH:MM:SS"
            if " " in date_str:
                date_str = date_str.split(" ")[0]
            
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%d/%m/%Y")
        
        return str(date_str)
    except Exception as e:
        # Si falla, devolver el string original
        return str(date_str) if date_str else "N/A"


def format_currency(amount: float, currency: str = "Bs.") -> str:
    """
    Formatea un monto como moneda
    
    Args:
        amount: Monto a formatear
        currency: Símbolo de moneda
    
    Returns:
        Monto formateado
    """
    return f"{currency} {amount:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Formatea un valor como porcentaje
    
    Args:
        value: Valor a formatear
        decimals: Número de decimales
    
    Returns:
        Valor formateado como porcentaje
    """
    return f"{value:.{decimals}f}%"

