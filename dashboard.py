import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Configuración de la página
st.set_page_config(page_title="Art Basel Hong Kong - Análisis de Ventas", layout="wide")

# Título y descripción
st.title("🎨 Art Basel Hong Kong - Dashboard de Ventas")
st.markdown("""
Este dashboard analiza las transacciones de arte en una de las ferias más importantes de Asia.
Explore las tendencias de mercado, artistas destacados y distribución de precios.
""")

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv('sales.csv')
    df['Precio Promedio'] = (df['Precio Mínimo'] + df['Precio Máximo']) / 2
    
    # Crear rangos de precios actualizados
    df['Rango de Precios'] = pd.cut(
        df['Precio Promedio'],
        bins=[0, 10000, 50000, 200000, float('inf')],
        labels=['< $10K', '$10K - $50K', '$50K - $200K', '$200K+']
    )
    
    # Calcular métricas adicionales por artista
    artist_metrics = df.groupby('Artista').agg({
        'Precio Promedio': 'sum',
        'Artista': 'count'
    }).rename(columns={'Artista': 'Obras por Artista'})
    df['Promedio Obras por Artista'] = len(df) / len(artist_metrics)
    
    # Calcular métricas por galería
    gallery_metrics = df.groupby('Galería').agg({
        'Precio Promedio': 'sum',
        'Galería': 'count'
    }).rename(columns={'Galería': 'Obras por Galería'})
    df['Promedio Obras por Galería'] = len(df) / len(gallery_metrics)
    
    return df

df = load_data()

# Sección de KPIs Principales
st.header("📊 Métricas Principales del Mercado")

# Primera fila de KPIs - Métricas Generales
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total de Obras", f"{len(df):,}")
with col2:
    st.metric("Total de Artistas", f"{df['Artista'].nunique():,}")
with col3:
    st.metric("Total de Galerías", f"{df['Galería'].nunique():,}")
with col4:
    st.metric("Volumen Total", f"${df['Precio Promedio'].sum():,.0f}")

# Segunda fila - Métricas de Precios
col5, col6, col7, col8 = st.columns(4)
with col5:
    st.metric("Precio Promedio", f"${df['Precio Promedio'].mean():,.0f}")
with col6:
    st.metric("Precio Mediano", f"${df['Precio Promedio'].median():,.0f}")
with col7:
    st.metric("Precio Mínimo", f"${df['Precio Promedio'].min():,.0f}")
with col8:
    st.metric("Precio Máximo", f"${df['Precio Promedio'].max():,.0f}")

# Tercera fila - Métricas de Dispersión y Ratios
col9, col10, col11, col12 = st.columns(4)
with col9:
    st.metric("Desviación Estándar", f"${df['Precio Promedio'].std():,.0f}")
with col10:
    obras_por_artista = len(df) / df['Artista'].nunique()
    st.metric("Obras por Artista", f"{obras_por_artista:.1f}")
with col11:
    obras_por_galeria = len(df) / df['Galería'].nunique()
    st.metric("Obras por Galería", f"{obras_por_galeria:.1f}")
with col12:
    valor_por_obra = df['Precio Promedio'].sum() / len(df)
    st.metric("Valor por Obra", f"${valor_por_obra:,.0f}")

# Distribución de Precios
st.subheader("📈 Distribución de Precios")
# Crear histograma con plotly
fig_histogram = go.Figure(data=[go.Histogram(
    x=df['Precio Promedio'],
    nbinsx=30,
    name='Número de Obras',
    hovertemplate="Rango de Precio: $%{x:,.0f}<br>Número de Obras: %{y}"
)])

fig_histogram.update_layout(
    title="Distribución de Obras por Rango de Precio",
    xaxis_title="Precio de la Obra ($)",
    yaxis_title="Número de Obras",
    bargap=0.1,
    showlegend=False
)

# Añadir línea vertical en la media y mediana
fig_histogram.add_vline(
    x=df['Precio Promedio'].mean(),
    line_dash="dash",
    line_color="red",
    annotation_text="Precio Promedio",
    annotation_position="top"
)
fig_histogram.add_vline(
    x=df['Precio Promedio'].median(),
    line_dash="dash",
    line_color="green",
    annotation_text="Precio Mediano",
    annotation_position="bottom"
)

st.plotly_chart(fig_histogram, use_container_width=True)

# Análisis de Galerías
st.header("🏢 Análisis de Galerías")

# Preparar datos agregados de galerías (una sola vez)
gallery_metrics = df.groupby('Galería').agg({
    'Precio Promedio': ['sum', 'mean', 'count'],
    'Artista': 'nunique'
}).round(2)
gallery_metrics.columns = ['Valor Total', 'Precio Promedio', 'Número de Obras', 'Número de Artistas']
gallery_metrics['Obras por Artista'] = (gallery_metrics['Número de Obras'] / gallery_metrics['Número de Artistas']).round(2)
gallery_metrics = gallery_metrics.sort_values('Valor Total', ascending=False)

# Visualizaciones principales de galerías
col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 Top 10 Galerías por Valor Total")
    fig_top_galleries = go.Figure(data=[
        go.Bar(
            x=gallery_metrics['Valor Total'].head(10).index,
            y=gallery_metrics['Valor Total'].head(10),
            text=gallery_metrics['Valor Total'].head(10).apply(lambda x: f'${x:,.0f}'),
            textposition='auto',
        )
    ])
    fig_top_galleries.update_layout(
        xaxis_title="Galería",
        yaxis_title="Valor Total ($)",
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_top_galleries, use_container_width=True)

with col2:
    st.subheader("📊 Obras y Artistas por Galería")
    fig_obras_artistas = go.Figure(data=[
        go.Bar(
            name='Obras',
            x=gallery_metrics['Número de Obras'].head(10).index,
            y=gallery_metrics['Número de Obras'].head(10),
            text=gallery_metrics['Número de Obras'].head(10).apply(lambda x: f'{x:,.0f}'),
        ),
        go.Bar(
            name='Artistas',
            x=gallery_metrics['Número de Artistas'].head(10).index,
            y=gallery_metrics['Número de Artistas'].head(10),
            text=gallery_metrics['Número de Artistas'].head(10).apply(lambda x: f'{x:,.0f}'),
        )
    ])
    fig_obras_artistas.update_layout(
        barmode='group',
        xaxis_title="Galería",
        yaxis_title="Cantidad",
        height=400
    )
    st.plotly_chart(fig_obras_artistas, use_container_width=True)

# Métricas resumen de galerías
col3, col4, col5, col6 = st.columns(4)
with col3:
    st.metric("Promedio Obras/Galería", f"{gallery_metrics['Número de Obras'].mean():.1f}")
with col4:
    st.metric("Promedio Artistas/Galería", f"{gallery_metrics['Número de Artistas'].mean():.1f}")
with col5:
    st.metric("Promedio Valor/Galería", f"${gallery_metrics['Valor Total'].mean():,.0f}")
with col6:
    st.metric("Promedio Obras/Artista", f"{gallery_metrics['Obras por Artista'].mean():.1f}")

# Scatter plot de relación Obras vs Valor Total
st.subheader("📈 Relación entre Número de Obras y Valor Total")
fig_scatter = go.Figure(data=[
    go.Scatter(
        x=gallery_metrics['Número de Obras'],
        y=gallery_metrics['Valor Total'],
        mode='markers+text',
        text=gallery_metrics.index,
        textposition="top center",
        hovertemplate="<b>%{text}</b><br>" +
                      "Número de Obras: %{x}<br>" +
                      "Valor Total: $%{y:,.0f}<br>",
        marker=dict(
            size=10,
            color=gallery_metrics['Precio Promedio'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Precio Promedio ($)")
        )
    )
])
fig_scatter.update_layout(
    height=500,
    xaxis_title="Número de Obras",
    yaxis_title="Valor Total ($)",
)
st.plotly_chart(fig_scatter, use_container_width=True)

# Tabla detallada en un expander
with st.expander("📋 Ver Detalles Completos de Galerías"):
    st.dataframe(
        gallery_metrics.style.format({
            'Valor Total': '${:,.2f}',
            'Precio Promedio': '${:,.2f}',
            'Número de Obras': '{:,.0f}',
            'Número de Artistas': '{:,.0f}',
            'Obras por Artista': '{:,.2f}'
        }),
        height=400
    )

# Análisis de Artistas
st.header("👨‍🎨 Análisis de Artistas")

# Preparar datos agregados de artistas
artist_metrics = df.groupby('Artista').agg({
    'Precio Promedio': ['sum', 'mean', 'count'],
    'Galería': 'nunique'
}).round(2)
artist_metrics.columns = ['Valor Total', 'Precio Promedio', 'Número de Obras', 'Número de Galerías']
artist_metrics = artist_metrics.sort_values('Valor Total', ascending=False)

# Métricas resumen de artistas
col_a1, col_a2, col_a3, col_a4 = st.columns(4)
with col_a1:
    st.metric("Promedio Obras/Artista", f"{artist_metrics['Número de Obras'].mean():.1f}")
with col_a2:
    st.metric("Promedio Galerías/Artista", f"{artist_metrics['Número de Galerías'].mean():.1f}")
with col_a3:
    st.metric("Promedio Valor/Artista", f"${artist_metrics['Valor Total'].mean():,.0f}")
with col_a4:
    artistas_exclusivos = len(artist_metrics[artist_metrics['Número de Galerías'] == 1])
    st.metric("Artistas Exclusivos", f"{artistas_exclusivos:,}")

# Visualizaciones principales de artistas
col_a5, col_a6 = st.columns(2)

with col_a5:
    st.subheader("💰 Top 10 Artistas por Valor Total")
    fig_top_artists = go.Figure(data=[
        go.Bar(
            x=artist_metrics['Valor Total'].head(10).index,
            y=artist_metrics['Valor Total'].head(10),
            text=artist_metrics['Valor Total'].head(10).apply(lambda x: f'${x:,.0f}'),
            textposition='auto',
        )
    ])
    fig_top_artists.update_layout(
        xaxis_title="Artista",
        yaxis_title="Valor Total ($)",
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_top_artists, use_container_width=True)

with col_a6:
    st.subheader("📊 Distribución de Obras por Artista")
    fig_obras_por_artista = go.Figure(data=[go.Histogram(
        x=artist_metrics['Número de Obras'],
        nbinsx=20,
        name='Número de Artistas',
        hovertemplate="Obras: %{x}<br>Número de Artistas: %{y}"
    )])
    fig_obras_por_artista.update_layout(
        xaxis_title="Número de Obras",
        yaxis_title="Número de Artistas",
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_obras_por_artista, use_container_width=True)

# Scatter plot de relación Obras vs Valor Total para Artistas
st.subheader("📈 Relación entre Número de Obras y Valor Total por Artista")
fig_scatter_artist = go.Figure(data=[
    go.Scatter(
        x=artist_metrics['Número de Obras'],
        y=artist_metrics['Valor Total'],
        mode='markers',
        text=artist_metrics.index,
        hovertemplate="<b>%{text}</b><br>" +
                     "Número de Obras: %{x}<br>" +
                     "Valor Total: $%{y:,.0f}<br>" +
                     "Precio Promedio: $%{marker.color:,.0f}<br>",
        marker=dict(
            size=10,
            color=artist_metrics['Precio Promedio'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Precio Promedio ($)")
        )
    )
])
fig_scatter_artist.update_layout(
    height=500,
    xaxis_title="Número de Obras",
    yaxis_title="Valor Total ($)",
)
st.plotly_chart(fig_scatter_artist, use_container_width=True)

# Análisis de Diversificación de Artistas
st.subheader("🎨 Diversificación de Artistas por Galerías")
fig_diversification = go.Figure(data=[go.Histogram(
    x=artist_metrics['Número de Galerías'],
    nbinsx=10,
    name='Número de Artistas',
    hovertemplate="Galerías: %{x}<br>Número de Artistas: %{y}"
)])
fig_diversification.update_layout(
    xaxis_title="Número de Galerías que Representan al Artista",
    yaxis_title="Número de Artistas",
    showlegend=False,
    height=400
)
st.plotly_chart(fig_diversification, use_container_width=True)

# Tabla detallada de artistas en un expander
with st.expander("📋 Ver Detalles Completos de Artistas"):
    st.dataframe(
        artist_metrics.style.format({
            'Valor Total': '${:,.2f}',
            'Precio Promedio': '${:,.2f}',
            'Número de Obras': '{:,.0f}',
            'Número de Galerías': '{:,.0f}'
        }),
        height=400
    )

# Tendencia Temporal de Obras
st.header("📅 Análisis Temporal")

# Preparar datos temporales
df['Año'] = pd.to_numeric(df['Año'], errors='coerce')
year_stats = df.groupby('Año').agg({
    'Precio Promedio': ['mean', 'sum', 'count'],
    'Artista': 'nunique',
    'Galería': 'nunique'
}).round(2)
year_stats.columns = ['Precio Promedio', 'Valor Total', 'Número de Obras', 'Número de Artistas', 'Número de Galerías']

# Métricas temporales
col_t1, col_t2, col_t3, col_t4 = st.columns(4)
with col_t1:
    crecimiento_obras = ((year_stats['Número de Obras'].iloc[-1] / year_stats['Número de Obras'].iloc[0]) - 1) * 100
    st.metric("Crecimiento en Obras", f"{crecimiento_obras:.1f}%")
with col_t2:
    crecimiento_precio = ((year_stats['Precio Promedio'].iloc[-1] / year_stats['Precio Promedio'].iloc[0]) - 1) * 100
    st.metric("Crecimiento en Precio", f"{crecimiento_precio:.1f}%")
with col_t3:
    crecimiento_artistas = ((year_stats['Número de Artistas'].iloc[-1] / year_stats['Número de Artistas'].iloc[0]) - 1) * 100
    st.metric("Crecimiento en Artistas", f"{crecimiento_artistas:.1f}%")
with col_t4:
    crecimiento_galerias = ((year_stats['Número de Galerías'].iloc[-1] / year_stats['Número de Galerías'].iloc[0]) - 1) * 100
    st.metric("Crecimiento en Galerías", f"{crecimiento_galerias:.1f}%")

# Visualizaciones temporales
col_t5, col_t6 = st.columns(2)

with col_t5:
    st.subheader("📈 Evolución de Precios y Obras")
    fig_temporal = go.Figure()
    
    # Añadir línea de precio promedio
    fig_temporal.add_trace(
        go.Scatter(
            x=year_stats.index,
            y=year_stats['Precio Promedio'],
            name='Precio Promedio',
            line=dict(color='blue'),
            yaxis='y1'
        )
    )
    
    # Añadir barras de número de obras
    fig_temporal.add_trace(
        go.Bar(
            x=year_stats.index,
            y=year_stats['Número de Obras'],
            name='Número de Obras',
            yaxis='y2',
            marker_color='lightblue',
            opacity=0.7
        )
    )
    
    fig_temporal.update_layout(
        yaxis=dict(
            title="Precio Promedio ($)",
            titlefont=dict(color="blue"),
            tickfont=dict(color="blue")
        ),
        yaxis2=dict(
            title="Número de Obras",
            titlefont=dict(color="lightblue"),
            tickfont=dict(color="lightblue"),
            overlaying="y",
            side="right"
        ),
        xaxis_title="Año",
        hovermode='x unified',
        showlegend=True,
        height=400
    )
    st.plotly_chart(fig_temporal, use_container_width=True)

with col_t6:
    st.subheader("📊 Evolución de Artistas y Galerías")
    fig_participantes = go.Figure()
    
    # Añadir línea de artistas
    fig_participantes.add_trace(
        go.Scatter(
            x=year_stats.index,
            y=year_stats['Número de Artistas'],
            name='Artistas',
            line=dict(color='green'),
            mode='lines+markers'
        )
    )
    
    # Añadir línea de galerías
    fig_participantes.add_trace(
        go.Scatter(
            x=year_stats.index,
            y=year_stats['Número de Galerías'],
            name='Galerías',
            line=dict(color='red'),
            mode='lines+markers'
        )
    )
    
    fig_participantes.update_layout(
        yaxis_title="Número de Participantes",
        xaxis_title="Año",
        hovermode='x unified',
        height=400
    )
    st.plotly_chart(fig_participantes, use_container_width=True)

# Tabla detallada temporal en un expander
with st.expander("📋 Ver Detalles Completos por Año"):
    st.dataframe(
        year_stats.style.format({
            'Precio Promedio': '${:,.2f}',
            'Valor Total': '${:,.2f}',
            'Número de Obras': '{:,.0f}',
            'Número de Artistas': '{:,.0f}',
            'Número de Galerías': '{:,.0f}'
        }),
        height=400
    )

# Análisis de Mercado
st.header("🌎 Análisis de Mercado")

# Preparar datos de segmentación
df['Segmento de Precio'] = pd.qcut(
    df['Precio Promedio'],
    q=4,
    labels=['Básico', 'Medio', 'Premium', 'Ultra Premium']
)

premium_threshold = df['Precio Promedio'].quantile(0.9)
premium_works = df[df['Precio Promedio'] > premium_threshold]

# Primera fila - Métricas de Segmentación
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    precio_medio_premium = premium_works['Precio Promedio'].mean()
    st.metric("Precio Medio Premium", f"${precio_medio_premium:,.0f}")
with col_m2:
    obras_premium = len(premium_works)
    st.metric("Obras Premium (Top 10%)", f"{obras_premium:,}")
with col_m3:
    valor_premium = premium_works['Precio Promedio'].sum()
    st.metric("Valor Total Premium", f"${valor_premium:,.0f}")
with col_m4:
    participacion_premium = (valor_premium / df['Precio Promedio'].sum()) * 100
    st.metric("% Valor Premium", f"{participacion_premium:.1f}%")

# Segunda fila - Análisis por Segmento
col_m5, col_m6 = st.columns(2)

with col_m5:
    st.subheader("📊 Distribución por Segmento de Precio")
    segment_stats = df.groupby('Segmento de Precio').agg({
        'Precio Promedio': ['count', 'mean', 'sum']
    }).round(2)
    segment_stats.columns = ['Número de Obras', 'Precio Promedio', 'Valor Total']
    
    # Calcular porcentajes
    segment_stats['% Obras'] = (segment_stats['Número de Obras'] / segment_stats['Número de Obras'].sum()) * 100
    segment_stats['% Valor'] = (segment_stats['Valor Total'] / segment_stats['Valor Total'].sum()) * 100
    
    fig_segments = go.Figure(data=[
        go.Bar(
            name='% Obras',
            x=segment_stats.index,
            y=segment_stats['% Obras'],
            text=segment_stats['% Obras'].apply(lambda x: f'{x:.1f}%'),
            textposition='auto',
        ),
        go.Bar(
            name='% Valor',
            x=segment_stats.index,
            y=segment_stats['% Valor'],
            text=segment_stats['% Valor'].apply(lambda x: f'{x:.1f}%'),
            textposition='auto',
        )
    ])
    
    fig_segments.update_layout(
        barmode='group',
        xaxis_title="Segmento",
        yaxis_title="Porcentaje (%)",
        height=400
    )
    st.plotly_chart(fig_segments, use_container_width=True)

with col_m6:
    st.subheader("💰 Precio Promedio por Segmento")
    fig_precio_segmento = go.Figure(data=[
        go.Bar(
            x=segment_stats.index,
            y=segment_stats['Precio Promedio'],
            text=segment_stats['Precio Promedio'].apply(lambda x: f'${x:,.0f}'),
            textposition='auto',
        )
    ])
    
    fig_precio_segmento.update_layout(
        xaxis_title="Segmento",
        yaxis_title="Precio Promedio ($)",
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_precio_segmento, use_container_width=True)

# Análisis Regional si existe la columna País
if 'País' in df.columns:
    st.subheader("🌍 Análisis Regional")
    
    # Preparar datos regionales
    region_stats = df.groupby('País').agg({
        'Precio Promedio': ['count', 'mean', 'sum'],
        'Artista': 'nunique',
        'Galería': 'nunique'
    }).round(2)
    region_stats.columns = ['Número de Obras', 'Precio Promedio', 'Valor Total', 'Número de Artistas', 'Número de Galerías']
    
    col_m7, col_m8 = st.columns(2)
    
    with col_m7:
        st.subheader("📊 Participación por País")
        region_stats['% Valor'] = (region_stats['Valor Total'] / region_stats['Valor Total'].sum()) * 100
        
        fig_regions = go.Figure(data=[
            go.Pie(
                labels=region_stats.index,
                values=region_stats['Valor Total'],
                textinfo='label+percent',
                hovertemplate="País: %{label}<br>Valor Total: $%{value:,.0f}<br>Porcentaje: %{percent}"
            )
        ])
        
        fig_regions.update_layout(height=400)
        st.plotly_chart(fig_regions, use_container_width=True)
    
    with col_m8:
        st.subheader("🎨 Precio Promedio por País")
        fig_precio_pais = go.Figure(data=[
            go.Bar(
                x=region_stats.index,
                y=region_stats['Precio Promedio'],
                text=region_stats['Precio Promedio'].apply(lambda x: f'${x:,.0f}'),
                textposition='auto',
            )
        ])
        
        fig_precio_pais.update_layout(
            xaxis_title="País",
            yaxis_title="Precio Promedio ($)",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_precio_pais, use_container_width=True)

# Análisis por Tipo de Artista si existe la columna
if 'Tipo_Artista' in df.columns:
    st.subheader("👨‍🎨 Análisis por Tipo de Artista")
    
    # Preparar datos por tipo de artista
    artist_type_stats = df.groupby('Tipo_Artista').agg({
        'Precio Promedio': ['count', 'mean', 'sum'],
        'Artista': 'nunique'
    }).round(2)
    artist_type_stats.columns = ['Número de Obras', 'Precio Promedio', 'Valor Total', 'Número de Artistas']
    
    col_m9, col_m10 = st.columns(2)
    
    with col_m9:
        st.subheader("📊 Distribución por Tipo de Artista")
        artist_type_stats['% Valor'] = (artist_type_stats['Valor Total'] / artist_type_stats['Valor Total'].sum()) * 100
        
        fig_artist_type = go.Figure(data=[
            go.Pie(
                labels=artist_type_stats.index,
                values=artist_type_stats['Valor Total'],
                textinfo='label+percent',
                hovertemplate="Tipo: %{label}<br>Valor Total: $%{value:,.0f}<br>Porcentaje: %{percent}"
            )
        ])
        
        fig_artist_type.update_layout(height=400)
        st.plotly_chart(fig_artist_type, use_container_width=True)
    
    with col_m10:
        st.subheader("💰 Métricas por Tipo de Artista")
        st.dataframe(
            artist_type_stats.style.format({
                'Número de Obras': '{:,.0f}',
                'Precio Promedio': '${:,.2f}',
                'Valor Total': '${:,.2f}',
                'Número de Artistas': '{:,.0f}',
                '% Valor': '{:.1f}%'
            }),
            height=400
        )

# Análisis de Estado de Venta si existe la columna
if 'Estado_Venta' in df.columns:
    st.subheader("📦 Análisis de Ventas")
    
    # Preparar datos de ventas
    ventas_stats = df.groupby('Estado_Venta').agg({
        'Precio Promedio': ['count', 'mean', 'sum']
    }).round(2)
    ventas_stats.columns = ['Número de Obras', 'Precio Promedio', 'Valor Total']
    
    col_m11, col_m12 = st.columns(2)
    
    with col_m11:
        total_obras = len(df)
        obras_vendidas = len(df[df['Estado_Venta'] == 'Vendida'])
        tasa_venta = (obras_vendidas / total_obras) * 100
        
        fig_ventas = go.Figure(data=[
            go.Pie(
                labels=['Vendidas', 'No Vendidas'],
                values=[obras_vendidas, total_obras - obras_vendidas],
                textinfo='label+percent',
                hole=.3
            )
        ])
        
        fig_ventas.update_layout(
            title="Estado de Ventas",
            height=400
        )
        st.plotly_chart(fig_ventas, use_container_width=True)
    
    with col_m12:
        st.metric("Tasa de Venta", f"{tasa_venta:.1f}%")
        st.metric("Obras Vendidas", f"{obras_vendidas:,}")
        st.metric("Valor Total Vendido", f"${ventas_stats.loc['Vendida', 'Valor Total']:,.0f}")

# Tabla detallada de segmentos en un expander
with st.expander("📋 Ver Detalles Completos por Segmento"):
    st.dataframe(
        segment_stats.style.format({
            'Número de Obras': '{:,.0f}',
            'Precio Promedio': '${:,.2f}',
            'Valor Total': '${:,.2f}',
            '% Obras': '{:.1f}%',
            '% Valor': '{:.1f}%'
        }),
        height=400
    )

# Sección de Filtros y Datos Filtrados
st.header("🔍 Filtros y Exploración de Datos")
st.markdown("""
Utilice los siguientes filtros para explorar los datos en detalle. 
Los filtros se aplicarán a la tabla de datos que se muestra a continuación.
""")

# Contenedor para los filtros
with st.container():
    # Primera fila de filtros
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        st.subheader("🏢 Filtro por Galería")
        selected_gallery = st.multiselect(
            "Seleccionar Galerías",
            options=sorted(df['Galería'].unique()),
            default=[]
        )
    
    with col_f2:
        st.subheader("💰 Filtro por Rango de Precios")
        min_price = float(df['Precio Promedio'].min())
        max_price = float(df['Precio Promedio'].max())
        price_range = st.slider(
            "Seleccionar Rango de Precios",
            min_value=min_price,
            max_value=max_price,
            value=(min_price, max_price),
            step=1000.0,  # Paso de 1000 para evitar decimales innecesarios
            help="Deslice para seleccionar el rango de precios"
        )
        st.caption(f"Rango seleccionado: ${price_range[0]:,.0f} - ${price_range[1]:,.0f}")
    
    with col_f3:
        st.subheader("📊 Filtro por Segmento")
        selected_price_range = st.multiselect(
            "Seleccionar Segmentos de Precio",
            options=sorted(df['Segmento de Precio'].unique()),
            default=[]
        )

    # Filtros adicionales si existen las columnas
    col_f4, col_f5, col_f6 = st.columns(3)
    
    with col_f4:
        if 'País' in df.columns:
            st.subheader("🌍 Filtro por País")
            selected_country = st.multiselect(
                "Seleccionar Países",
                options=sorted(df['País'].unique()),
                default=[]
            )
    
    with col_f5:
        if 'Tipo_Artista' in df.columns:
            st.subheader("👨‍🎨 Filtro por Tipo de Artista")
            selected_artist_type = st.multiselect(
                "Seleccionar Tipos de Artista",
                options=sorted(df['Tipo_Artista'].unique()),
                default=[]
            )
    
    with col_f6:
        if 'Estado_Venta' in df.columns:
            st.subheader("📦 Filtro por Estado de Venta")
            selected_sale_status = st.multiselect(
                "Seleccionar Estado de Venta",
                options=sorted(df['Estado_Venta'].unique()),
                default=[]
            )

# Aplicar filtros
mask = pd.Series(True, index=df.index)

if selected_gallery:
    mask &= df['Galería'].isin(selected_gallery)

mask &= (df['Precio Promedio'] >= price_range[0]) & (df['Precio Promedio'] <= price_range[1])

if selected_price_range:
    mask &= df['Segmento de Precio'].isin(selected_price_range)

if 'País' in df.columns and selected_country:
    mask &= df['País'].isin(selected_country)

if 'Tipo_Artista' in df.columns and selected_artist_type:
    mask &= df['Tipo_Artista'].isin(selected_artist_type)

if 'Estado_Venta' in df.columns and selected_sale_status:
    mask &= df['Estado_Venta'].isin(selected_sale_status)

df_filtered = df[mask]

# Mostrar resumen de filtros aplicados
st.subheader("📊 Resumen de Filtros Aplicados")
col_f7, col_f8, col_f9, col_f10 = st.columns(4)

with col_f7:
    st.metric("Obras Seleccionadas", f"{len(df_filtered):,}")
with col_f8:
    st.metric("Galerías Seleccionadas", f"{df_filtered['Galería'].nunique():,}")
with col_f9:
    st.metric("Artistas Seleccionados", f"{df_filtered['Artista'].nunique():,}")
with col_f10:
    valor_filtrado = df_filtered['Precio Promedio'].sum()
    st.metric("Valor Total Filtrado", f"${valor_filtrado:,.0f}")

# Mostrar datos filtrados
st.subheader("🎨 Obras Filtradas")
with st.expander("Ver Datos Filtrados", expanded=True):
    st.dataframe(
        df_filtered.style.format({
            'Precio Mínimo': '${:,.2f}',
            'Precio Máximo': '${:,.2f}',
            'Precio Promedio': '${:,.2f}'
        }),
        height=400
    ) 