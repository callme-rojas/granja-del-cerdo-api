"""
Sistema de Gráficos Profesionales con Plotly
Visualizaciones interactivas modernas tipo SaaS
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Dict, Optional, Any
import streamlit as st


# Paleta de colores profesional
COLORS = {
    "primary": ["#3B82F6", "#2563EB", "#1D4ED8", "#1E40AF", "#1E3A8A"],
    "success": ["#10B981", "#059669", "#047857", "#065F46", "#064E3B"],
    "warning": ["#F59E0B", "#D97706", "#B45309", "#92400E", "#78350F"],
    "error": ["#EF4444", "#DC2626", "#B91C1C", "#991B1B", "#7F1D1D"],
    "info": ["#06B6D4", "#0891B2", "#0E7490", "#155E75", "#164E63"],
    "gradient": ["#3B82F6", "#8B5CF6", "#EC4899", "#EF4444", "#F59E0B"],
}

# Configuración de tema profesional
LAYOUT_CONFIG = {
    "font": {"family": "Inter, -apple-system, BlinkMacSystemFont, sans-serif", "size": 12},
    "plot_bgcolor": "white",
    "paper_bgcolor": "white",
    "margin": {"l": 40, "r": 40, "t": 60, "b": 40},
    "hovermode": "x unified",
    "hoverlabel": {
        "bgcolor": "white",
        "font_size": 13,
        "font_family": "Inter, sans-serif"
    },
}


def apply_professional_theme(fig: go.Figure, title: str = "") -> go.Figure:
    """
    Aplica tema profesional a una figura de Plotly
    
    Args:
        fig: Figura de Plotly
        title: Título del gráfico
    
    Returns:
        Figura con tema aplicado
    """
    fig.update_layout(
        **LAYOUT_CONFIG,
        title={
            "text": title,
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 18, "weight": "bold", "color": "#1F2937"}
        },
        xaxis={
            "showgrid": True,
            "gridwidth": 1,
            "gridcolor": "#F3F4F6",
            "zeroline": False,
            "showline": True,
            "linewidth": 2,
            "linecolor": "#E5E7EB"
        },
        yaxis={
            "showgrid": True,
            "gridwidth": 1,
            "gridcolor": "#F3F4F6",
            "zeroline": False,
            "showline": True,
            "linewidth": 2,
            "linecolor": "#E5E7EB"
        }
    )
    
    return fig


def line_chart(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str = "",
    color: str = "primary",
    show_markers: bool = True,
    fill_area: bool = True
) -> go.Figure:
    """
    Gráfico de líneas profesional
    
    Args:
        data: DataFrame con los datos
        x_col: Columna para eje X
        y_col: Columna para eje Y
        title: Título del gráfico
        color: Color del gráfico
        show_markers: Mostrar marcadores en los puntos
        fill_area: Rellenar área bajo la línea
    """
    fig = go.Figure()
    
    main_color = COLORS[color][0]
    
    fig.add_trace(go.Scatter(
        x=data[x_col],
        y=data[y_col],
        mode='lines+markers' if show_markers else 'lines',
        name=y_col,
        line=dict(color=main_color, width=3),
        marker=dict(size=8, color=main_color),
        fill='tozeroy' if fill_area else None,
        fillcolor=f'rgba({int(main_color[1:3], 16)}, {int(main_color[3:5], 16)}, {int(main_color[5:7], 16)}, 0.1)'
    ))
    
    fig = apply_professional_theme(fig, title)
    
    return fig


def bar_chart(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str = "",
    color: str = "primary",
    show_values: bool = True,
    horizontal: bool = False
) -> go.Figure:
    """
    Gráfico de barras profesional
    
    Args:
        data: DataFrame con los datos
        x_col: Columna para eje X
        y_col: Columna para eje Y
        title: Título del gráfico
        color: Color del gráfico
        show_values: Mostrar valores sobre las barras
        horizontal: Gráfico horizontal
    """
    fig = go.Figure()
    
    colors_list = COLORS[color]
    
    if horizontal:
        fig.add_trace(go.Bar(
            y=data[x_col],
            x=data[y_col],
            orientation='h',
            marker=dict(
                color=colors_list[0],
                line=dict(color='white', width=2)
            ),
            text=data[y_col] if show_values else None,
            textposition='outside'
        ))
    else:
        fig.add_trace(go.Bar(
            x=data[x_col],
            y=data[y_col],
            marker=dict(
                color=colors_list,
                line=dict(color='white', width=2)
            ),
            text=data[y_col] if show_values else None,
            textposition='outside'
        ))
    
    fig = apply_professional_theme(fig, title)
    
    return fig


def pie_chart(
    labels: List[str],
    values: List[float],
    title: str = "",
    colors: List[str] = None,
    show_legend: bool = True,
    donut: bool = True
) -> go.Figure:
    """
    Gráfico circular profesional
    
    Args:
        labels: Etiquetas de las categorías
        values: Valores de cada categoría
        title: Título del gráfico
        colors: Lista de colores personalizados
        show_legend: Mostrar leyenda
        donut: Mostrar como donut (con agujero central)
    """
    fig = go.Figure()
    
    if colors is None:
        colors = COLORS["gradient"]
    
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=0.4 if donut else 0,
        marker=dict(colors=colors, line=dict(color='white', width=2)),
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+value+percent',
        textfont=dict(size=13, color='white', weight='bold')
    ))
    
    fig.update_layout(
        **LAYOUT_CONFIG,
        title={
            "text": title,
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 18, "weight": "bold", "color": "#1F2937"}
        },
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig


def area_chart(
    data: pd.DataFrame,
    x_col: str,
    y_cols: List[str],
    title: str = "",
    colors: List[str] = None,
    stacked: bool = False
) -> go.Figure:
    """
    Gráfico de área profesional con múltiples series
    
    Args:
        data: DataFrame con los datos
        x_col: Columna para eje X
        y_cols: Lista de columnas para eje Y
        title: Título del gráfico
        colors: Lista de colores personalizados
        stacked: Apilar las áreas
    """
    fig = go.Figure()
    
    if colors is None:
        colors = COLORS["primary"]
    
    for i, y_col in enumerate(y_cols):
        color = colors[i % len(colors)]
        
        fig.add_trace(go.Scatter(
            x=data[x_col],
            y=data[y_col],
            mode='lines',
            name=y_col,
            line=dict(color=color, width=2),
            fill='tonexty' if stacked and i > 0 else 'tozeroy',
            fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.3)',
            stackgroup='one' if stacked else None
        ))
    
    fig = apply_professional_theme(fig, title)
    
    return fig


def multi_line_chart(
    data: pd.DataFrame,
    x_col: str,
    y_cols: List[str],
    title: str = "",
    colors: List[str] = None
) -> go.Figure:
    """
    Gráfico de múltiples líneas profesional
    
    Args:
        data: DataFrame con los datos
        x_col: Columna para eje X
        y_cols: Lista de columnas para eje Y
        title: Título del gráfico
        colors: Lista de colores personalizados
    """
    fig = go.Figure()
    
    if colors is None:
        colors = COLORS["gradient"]
    
    for i, y_col in enumerate(y_cols):
        color = colors[i % len(colors)]
        
        fig.add_trace(go.Scatter(
            x=data[x_col],
            y=data[y_col],
            mode='lines+markers',
            name=y_col,
            line=dict(color=color, width=3),
            marker=dict(size=8, color=color)
        ))
    
    fig = apply_professional_theme(fig, title)
    
    return fig


def gauge_chart(
    value: float,
    max_value: float = 100,
    title: str = "",
    color: str = "primary",
    thresholds: Optional[Dict[str, float]] = None
) -> go.Figure:
    """
    Gráfico de gauge (medidor) profesional
    
    Args:
        value: Valor actual
        max_value: Valor máximo
        title: Título del gráfico
        color: Color principal
        thresholds: Umbrales para colores (ej: {"low": 30, "medium": 70})
    """
    # Determinar color según umbrales
    if thresholds:
        if value < thresholds.get("low", 30):
            gauge_color = COLORS["error"][0]
        elif value < thresholds.get("medium", 70):
            gauge_color = COLORS["warning"][0]
        else:
            gauge_color = COLORS["success"][0]
    else:
        gauge_color = COLORS[color][0]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 18, 'color': '#1F2937'}},
        gauge={
            'axis': {'range': [None, max_value], 'tickwidth': 1, 'tickcolor': "#E5E7EB"},
            'bar': {'color': gauge_color, 'thickness': 0.75},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#E5E7EB",
            'steps': [
                {'range': [0, max_value * 0.3], 'color': '#FEE2E2'},
                {'range': [max_value * 0.3, max_value * 0.7], 'color': '#FEF3C7'},
                {'range': [max_value * 0.7, max_value], 'color': '#D1FAE5'}
            ],
        }
    ))
    
    fig.update_layout(
        **LAYOUT_CONFIG,
        height=300
    )
    
    return fig


def heatmap_chart(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    z_col: str,
    title: str = "",
    colorscale: str = "Blues"
) -> go.Figure:
    """
    Mapa de calor profesional
    
    Args:
        data: DataFrame con los datos
        x_col: Columna para eje X
        y_col: Columna para eje Y
        z_col: Columna para valores (color)
        title: Título del gráfico
        colorscale: Escala de colores
    """
    pivot_data = data.pivot_table(
        values=z_col,
        index=y_col,
        columns=x_col,
        aggfunc='sum'
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale=colorscale,
        text=pivot_data.values,
        texttemplate='%{text}',
        textfont={"size": 12},
        hovertemplate='%{x}<br>%{y}<br>Valor: %{z}<extra></extra>'
    ))
    
    fig = apply_professional_theme(fig, title)
    
    return fig


def sparkline_chart(data: List[float], color: str = "#3B82F6") -> go.Figure:
    """
    Mini gráfico sparkline para métricas
    
    Args:
        data: Lista de valores
        color: Color de la línea
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        y=data,
        mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2)',
        hoverinfo='y'
    ))
    
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=60,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def combo_chart(
    data: pd.DataFrame,
    x_col: str,
    bar_cols: List[str],
    line_cols: List[str],
    title: str = ""
) -> go.Figure:
    """
    Gráfico combinado de barras y líneas
    
    Args:
        data: DataFrame con los datos
        x_col: Columna para eje X
        bar_cols: Columnas para barras
        line_cols: Columnas para líneas
        title: Título del gráfico
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Agregar barras
    for i, col in enumerate(bar_cols):
        fig.add_trace(
            go.Bar(
                x=data[x_col],
                y=data[col],
                name=col,
                marker=dict(color=COLORS["primary"][i])
            ),
            secondary_y=False
        )
    
    # Agregar líneas
    for i, col in enumerate(line_cols):
        fig.add_trace(
            go.Scatter(
                x=data[x_col],
                y=data[col],
                name=col,
                mode='lines+markers',
                line=dict(color=COLORS["success"][i], width=3),
                marker=dict(size=8)
            ),
            secondary_y=True
        )
    
    fig = apply_professional_theme(fig, title)
    
    return fig


def display_chart(fig: go.Figure, use_container_width: bool = True):
    """
    Muestra un gráfico de Plotly en Streamlit con configuración profesional
    
    Args:
        fig: Figura de Plotly
        use_container_width: Usar ancho completo del contenedor
    """
    config = {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'chart',
            'height': 800,
            'width': 1200,
            'scale': 2
        }
    }
    
    st.plotly_chart(fig, use_container_width=use_container_width, config=config)

