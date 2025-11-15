"""
Sistema Avanzado de Gráficos Interactivos con Plotly
Visualizaciones profesionales con filtros, animaciones y alta interactividad
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Any
import streamlit as st


# Paleta de colores rosa pastel para tema oscuro
CORPORATE_COLORS = {
    "primary": "#FF91A4",      # Rosa pastel principal
    "secondary": "#FFB6C1",    # Rosa pastel claro
    "success": "#A8E6CF",      # Verde pastel
    "warning": "#FFD3A5",      # Naranja pastel
    "danger": "#FF9AA2",       # Rojo pastel
    "info": "#B5EAD7",         # Cyan pastel
    "neutral": "#9A9AAA",      # Gris claro
}

CHART_TEMPLATE = "plotly_dark"

# Configuración base para todos los gráficos
BASE_CONFIG = {
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'eraseshape'],
    'modeBarButtonsToRemove': ['pan2d', 'lasso2d'],
    'toImageButtonOptions': {
        'format': 'png',
        'filename': 'chart',
        'height': 1080,
        'width': 1920,
        'scale': 2
    }
}

def apply_corporate_layout(fig: go.Figure, title: str = "", height: int = 400) -> go.Figure:
    """Aplica diseño corporativo profesional con tema oscuro"""
    fig.update_layout(
        template=CHART_TEMPLATE,
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'weight': 'bold', 'color': '#FFFFFF', 'family': 'Arial, sans-serif'}
        },
        height=height,
        margin=dict(l=60, r=40, t=80, b=60),
        paper_bgcolor='#000000',
        plot_bgcolor='#0A0A0A',
        hovermode='x unified',
        font=dict(family='Arial, sans-serif', size=12, color='#E0E0E0'),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(255, 145, 164, 0.2)',
            zeroline=False,
            showline=True,
            linewidth=2,
            linecolor='#3A3A4A',
            title_font=dict(size=13, weight='bold', color='#FFFFFF')
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(255, 145, 164, 0.2)',
            zeroline=False,
            showline=True,
            linewidth=2,
            linecolor='#3A3A4A',
            title_font=dict(size=13, weight='bold', color='#FFFFFF')
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(10, 10, 10, 0.9)',
            bordercolor='#3A3A4A',
            borderwidth=1,
            font=dict(color='#FFFFFF')
        )
    )
    return fig


def interactive_line_chart(
    data: pd.DataFrame,
    x_col: str,
    y_cols: List[str],
    title: str = "",
    y_title: str = "",
    colors: Optional[List[str]] = None,
    show_range_selector: bool = True,
    enable_animations: bool = True
) -> go.Figure:
    """
    Gráfico de líneas interactivo profesional con selector de rango y filtros
    """
    fig = go.Figure()
    
    if colors is None:
        colors = [CORPORATE_COLORS["primary"], CORPORATE_COLORS["success"], 
                  CORPORATE_COLORS["warning"], CORPORATE_COLORS["danger"]]
    
    for i, y_col in enumerate(y_cols):
        color = colors[i % len(colors)]
        
        fig.add_trace(go.Scatter(
            x=data[x_col],
            y=data[y_col],
            name=y_col,
            mode='lines+markers',
            line=dict(color=color, width=3, shape='spline'),
            marker=dict(
                size=8,
                color=color,
                line=dict(width=2, color='white')
            ),
            hovertemplate='<b>%{x}</b><br>' +
                          f'{y_col}: %{{y:,.2f}}<br>' +
                          '<extra></extra>',
            connectgaps=True
        ))
    
    fig = apply_corporate_layout(fig, title, 450)
    
    fig.update_yaxes(title_text=y_title)
    
    # Range selector y slider para interactividad
    if show_range_selector:
        fig.update_xaxes(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all", label="Todo")
                ]),
                bgcolor='white',
                activecolor=CORPORATE_COLORS["primary"],
                x=0,
                y=1.1
            ),
            rangeslider=dict(visible=True, thickness=0.05),
            type="date"
        )
    
    return fig


def animated_bar_chart(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str = "",
    color_col: Optional[str] = None,
    orientation: str = 'v',
    show_values: bool = True
) -> go.Figure:
    """Gráfico de barras con animaciones y colores dinámicos"""
    
    if color_col:
        # Colores basados en valores
        colors = data[y_col].values
        colorscale = [[0, CORPORATE_COLORS["danger"]], 
                      [0.5, CORPORATE_COLORS["warning"]], 
                      [1, CORPORATE_COLORS["success"]]]
    else:
        colors = CORPORATE_COLORS["primary"]
        colorscale = None
    
    if orientation == 'v':
        fig = go.Figure(data=[
            go.Bar(
                x=data[x_col],
                y=data[y_col],
                marker=dict(
                    color=colors,
                    colorscale=colorscale,
                    line=dict(color='white', width=2),
                    cornerradius=5
                ),
                text=data[y_col] if show_values else None,
                texttemplate='%{text:,.0f}' if show_values else None,
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Valor: %{y:,.0f}<extra></extra>'
            )
        ])
    else:
        fig = go.Figure(data=[
            go.Bar(
                y=data[x_col],
                x=data[y_col],
                orientation='h',
                marker=dict(
                    color=colors,
                    colorscale=colorscale,
                    line=dict(color='white', width=2),
                    cornerradius=5
                ),
                text=data[y_col] if show_values else None,
                texttemplate='%{text:,.0f}' if show_values else None,
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Valor: %{x:,.0f}<extra></extra>'
            )
        ])
    
    fig = apply_corporate_layout(fig, title, 400)
    
    return fig


def interactive_donut_chart(
    labels: List[str],
    values: List[float],
    title: str = "",
    colors: Optional[List[str]] = None,
    height: int = 450
) -> go.Figure:
    """Gráfico donut interactivo con hover effects"""
    
    if colors is None:
        colors = [CORPORATE_COLORS["primary"], CORPORATE_COLORS["success"], 
                  CORPORATE_COLORS["warning"], CORPORATE_COLORS["info"]]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.5,
        marker=dict(
            colors=colors,
            line=dict(color='white', width=3)
        ),
        textinfo='label+percent',
        textfont=dict(size=13, color='white', weight='bold'),
        hovertemplate='<b>%{label}</b><br>' +
                      'Valor: Bs. %{value:,.2f}<br>' +
                      'Porcentaje: %{percent}<br>' +
                      '<extra></extra>',
        pull=[0.05] * len(labels)  # Separar ligeramente las secciones
    )])
    
    # Agregar anotación en el centro
    total = sum(values)
    fig.add_annotation(
        text=f'<b>Total</b><br>Bs. {total:,.2f}',
        x=0.5, y=0.5,
        font=dict(size=16, color='#1F2937', weight='bold'),
        showarrow=False
    )
    
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'weight': 'bold', 'color': '#1F2937'}
        },
        height=height,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.1
        ),
        paper_bgcolor='white',
        font=dict(family='Arial, sans-serif')
    )
    
    return fig


def multi_axis_chart(
    data: pd.DataFrame,
    x_col: str,
    y1_cols: List[str],
    y2_cols: List[str],
    title: str = "",
    y1_title: str = "Eje Izquierdo",
    y2_title: str = "Eje Derecho"
) -> go.Figure:
    """Gráfico con doble eje Y para comparar diferentes métricas"""
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Primer eje Y - Barras
    for i, col in enumerate(y1_cols):
        fig.add_trace(
            go.Bar(
                x=data[x_col],
                y=data[col],
                name=col,
                marker=dict(color=CORPORATE_COLORS["primary"], opacity=0.7),
                hovertemplate=f'<b>{col}</b><br>%{{y:,.0f}}<extra></extra>'
            ),
            secondary_y=False
        )
    
    # Segundo eje Y - Líneas
    for i, col in enumerate(y2_cols):
        fig.add_trace(
            go.Scatter(
                x=data[x_col],
                y=data[col],
                name=col,
                mode='lines+markers',
                line=dict(color=CORPORATE_COLORS["warning"], width=3),
                marker=dict(size=8),
                hovertemplate=f'<b>{col}</b><br>Bs. %{{y:,.2f}}<extra></extra>'
            ),
            secondary_y=True
        )
    
    fig.update_yaxes(title_text=y1_title, secondary_y=False)
    fig.update_yaxes(title_text=y2_title, secondary_y=True)
    
    fig = apply_corporate_layout(fig, title, 450)
    
    return fig


def scatter_with_regression(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str = "",
    size_col: Optional[str] = None,
    color_col: Optional[str] = None
) -> go.Figure:
    """Gráfico de dispersión con línea de regresión"""
    
    fig = go.Figure()
    
    # Calcular regresión lineal
    z = np.polyfit(data[x_col], data[y_col], 1)
    p = np.poly1d(z)
    x_line = np.linspace(data[x_col].min(), data[x_col].max(), 100)
    y_line = p(x_line)
    
    # Línea de regresión
    fig.add_trace(go.Scatter(
        x=x_line,
        y=y_line,
        mode='lines',
        name='Tendencia',
        line=dict(color=CORPORATE_COLORS["danger"], width=2, dash='dash'),
        hoverinfo='skip'
    ))
    
    # Puntos de datos
    marker_config = dict(
        size=data[size_col] if size_col else 12,
        color=data[color_col] if color_col else CORPORATE_COLORS["primary"],
        line=dict(width=2, color='white'),
        opacity=0.7
    )
    
    if color_col:
        marker_config['colorscale'] = 'Viridis'
        marker_config['showscale'] = True
        marker_config['colorbar'] = dict(title=color_col)
    
    fig.add_trace(go.Scatter(
        x=data[x_col],
        y=data[y_col],
        mode='markers',
        name='Datos',
        marker=marker_config,
        text=data.index,
        hovertemplate='<b>Lote %{text}</b><br>' +
                      f'{x_col}: %{{x:.2f}}<br>' +
                      f'{y_col}: %{{y:.2f}}<br>' +
                      '<extra></extra>'
    ))
    
    fig = apply_corporate_layout(fig, title, 450)
    fig.update_xaxes(title_text=x_col)
    fig.update_yaxes(title_text=y_col)
    
    return fig


def heatmap_calendar(
    data: pd.DataFrame,
    date_col: str,
    value_col: str,
    title: str = ""
) -> go.Figure:
    """Mapa de calor tipo calendario con interactividad"""
    
    # Preparar datos
    df = data.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df['week'] = df[date_col].dt.isocalendar().week
    df['day_of_week'] = df[date_col].dt.dayofweek
    df['month'] = df[date_col].dt.strftime('%Y-%m')
    
    pivot = df.pivot_table(
        values=value_col,
        index='day_of_week',
        columns='week',
        aggfunc='sum',
        fill_value=0
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
        colorscale=[
            [0, '#F3F4F6'],
            [0.5, CORPORATE_COLORS["warning"]],
            [1, CORPORATE_COLORS["success"]]
        ],
        text=pivot.values,
        texttemplate='%{text:.0f}',
        textfont={"size": 10},
        hovertemplate='Semana: %{x}<br>Día: %{y}<br>Valor: %{z:.0f}<extra></extra>',
        showscale=True,
        colorbar=dict(title=value_col)
    ))
    
    fig = apply_corporate_layout(fig, title, 350)
    fig.update_xaxes(title_text="Semana del Año")
    
    return fig


def funnel_chart(
    stages: List[str],
    values: List[float],
    title: str = ""
) -> go.Figure:
    """Gráfico de embudo para visualizar procesos"""
    
    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textposition="inside",
        textinfo="value+percent initial",
        marker=dict(
            color=[CORPORATE_COLORS["primary"], CORPORATE_COLORS["info"], 
                   CORPORATE_COLORS["success"], CORPORATE_COLORS["warning"]],
            line=dict(width=2, color='white')
        ),
        connector=dict(line=dict(color=CORPORATE_COLORS["neutral"], width=2)),
        hovertemplate='<b>%{y}</b><br>Valor: %{x:,.0f}<br>%{percentInitial}<extra></extra>'
    ))
    
    fig = apply_corporate_layout(fig, title, 400)
    
    return fig


def comparison_chart(
    categories: List[str],
    series_data: Dict[str, List[float]],
    title: str = "",
    chart_type: str = 'bar'
) -> go.Figure:
    """Gráfico de comparación entre múltiples series"""
    
    fig = go.Figure()
    
    colors = [CORPORATE_COLORS["primary"], CORPORATE_COLORS["success"], 
              CORPORATE_COLORS["warning"], CORPORATE_COLORS["info"]]
    
    for i, (series_name, values) in enumerate(series_data.items()):
        if chart_type == 'bar':
            fig.add_trace(go.Bar(
                name=series_name,
                x=categories,
                y=values,
                marker=dict(color=colors[i % len(colors)], cornerradius=5),
                hovertemplate=f'<b>{series_name}</b><br>%{{x}}: %{{y:,.0f}}<extra></extra>'
            ))
        else:  # line
            fig.add_trace(go.Scatter(
                name=series_name,
                x=categories,
                y=values,
                mode='lines+markers',
                line=dict(color=colors[i % len(colors)], width=3),
                marker=dict(size=8),
                hovertemplate=f'<b>{series_name}</b><br>%{{x}}: %{{y:,.0f}}<extra></extra>'
            ))
    
    fig.update_layout(barmode='group')
    fig = apply_corporate_layout(fig, title, 400)
    
    return fig


def kpi_gauge(
    value: float,
    title: str = "",
    max_value: float = 100,
    thresholds: Optional[Dict[str, float]] = None,
    suffix: str = ""
) -> go.Figure:
    """Gauge profesional tipo velocímetro para KPIs"""
    
    if thresholds is None:
        thresholds = {"low": 30, "medium": 70}
    
    # Determinar color según umbrales
    if value < thresholds["low"]:
        color = CORPORATE_COLORS["danger"]
    elif value < thresholds["medium"]:
        color = CORPORATE_COLORS["warning"]
    else:
        color = CORPORATE_COLORS["success"]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 18, 'color': '#1F2937', 'weight': 'bold'}},
        number={'suffix': suffix, 'font': {'size': 36, 'weight': 'bold'}},
        gauge={
            'axis': {
                'range': [None, max_value],
                'tickwidth': 2,
                'tickcolor': "#E5E7EB",
                'tickfont': {'size': 12}
            },
            'bar': {'color': color, 'thickness': 0.8},
            'bgcolor': "white",
            'borderwidth': 3,
            'bordercolor': "#E5E7EB",
            'steps': [
                {'range': [0, thresholds["low"]], 'color': 'rgba(239, 68, 68, 0.1)'},
                {'range': [thresholds["low"], thresholds["medium"]], 'color': 'rgba(245, 158, 11, 0.1)'},
                {'range': [thresholds["medium"], max_value], 'color': 'rgba(16, 185, 129, 0.1)'}
            ],
            'threshold': {
                'line': {'color': color, 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        paper_bgcolor='white',
        font={'family': 'Arial, sans-serif'}
    )
    
    return fig


def display_chart(fig: go.Figure, key: Optional[str] = None):
    """Muestra gráfico de Plotly en Streamlit con configuración óptima"""
    st.plotly_chart(
        fig,
        use_container_width=True,
        config=BASE_CONFIG,
        key=key
    )

