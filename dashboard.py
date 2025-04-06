import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Page configuration
st.set_page_config(page_title="Art Basel Hong Kong - Sales Analysis", layout="wide")

# Title and description
st.title("🎨 Art Basel Hong Kong - Sales Dashboard")
st.markdown("""
This dashboard analyses art transactions at one of Asia's most important fairs.
Explore market trends, featured artists and price distribution.
""")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('sales.csv')
    df['Average Price'] = (df['Minimum Price'] + df['Maximum Price']) / 2
    
    # Create updated price ranges
    df['Price Range'] = pd.cut(
        df['Average Price'],
        bins=[0, 10000, 50000, 200000, float('inf')],
        labels=['< $10K', '$10K - $50K', '$50K - $200K', '$200K+']
    )
    
    # Calculate additional metrics per artist
    artist_metrics = df.groupby('Artist').agg({
        'Average Price': 'sum',
        'Artist': 'count'
    }).rename(columns={'Artist': 'Works per Artist'})
    df['Average Works per Artist'] = len(df) / len(artist_metrics)
    
    # Calculate metrics per gallery
    gallery_metrics = df.groupby('Gallery').agg({
        'Average Price': 'sum',
        'Gallery': 'count'
    }).rename(columns={'Gallery': 'Works per Gallery'})
    df['Average Works per Gallery'] = len(df) / len(gallery_metrics)
    
    return df

df = load_data()

# Main KPIs Section
st.header("📊 Key Market Metrics")

# First row of KPIs - General Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Works", f"{len(df):,}")
with col2:
    st.metric("Total Artists", f"{df['Artist'].nunique():,}")
with col3:
    st.metric("Total Galleries", f"{df['Gallery'].nunique():,}")
with col4:
    st.metric("Total Volume", f"${df['Average Price'].sum():,.0f}")

# Second row - Price Metrics
col5, col6, col7, col8 = st.columns(4)
with col5:
    st.metric("Average Price", f"${df['Average Price'].mean():,.0f}")
with col6:
    st.metric("Median Price", f"${df['Average Price'].median():,.0f}")
with col7:
    st.metric("Minimum Price", f"${df['Average Price'].min():,.0f}")
with col8:
    st.metric("Maximum Price", f"${df['Average Price'].max():,.0f}")

# Third row - Dispersion Metrics and Ratios
col9, col10, col11, col12 = st.columns(4)
with col9:
    st.metric("Standard Deviation", f"${df['Average Price'].std():,.0f}")
with col10:
    works_per_artist = len(df) / df['Artist'].nunique()
    st.metric("Works per Artist", f"{works_per_artist:.1f}")
with col11:
    works_per_gallery = len(df) / df['Gallery'].nunique()
    st.metric("Works per Gallery", f"{works_per_gallery:.1f}")
with col12:
    value_per_work = df['Average Price'].sum() / len(df)
    st.metric("Value per Work", f"${value_per_work:,.0f}")

# Price Distribution
st.subheader("📈 Price Distribution")
# Create histogram with plotly
fig_histogram = go.Figure(data=[go.Histogram(
    x=df['Average Price'],
    nbinsx=30,
    name='Number of Works',
    hovertemplate="Price Range: $%{x:,.0f}<br>Number of Works: %{y}"
)])

fig_histogram.update_layout(
    title="Distribution of Works by Price Range",
    xaxis_title="Work Price ($)",
    yaxis_title="Number of Works",
    bargap=0.1,
    showlegend=False
)

# Add vertical lines for mean and median
fig_histogram.add_vline(
    x=df['Average Price'].mean(),
    line_dash="dash",
    line_color="red",
    annotation_text="Average Price",
    annotation_position="top"
)
fig_histogram.add_vline(
    x=df['Average Price'].median(),
    line_dash="dash",
    line_color="green",
    annotation_text="Median Price",
    annotation_position="bottom"
)

st.plotly_chart(fig_histogram, use_container_width=True)

# Gallery Analysis
st.header("🏢 Gallery Analysis")

# Prepare aggregated gallery data (once)
gallery_metrics = df.groupby('Gallery').agg({
    'Average Price': ['sum', 'mean', 'count'],
    'Artist': 'nunique'
}).round(2)
gallery_metrics.columns = ['Total Value', 'Average Price', 'Number of Works', 'Number of Artists']
gallery_metrics['Works per Artist'] = (gallery_metrics['Number of Works'] / gallery_metrics['Number of Artists']).round(2)
gallery_metrics = gallery_metrics.sort_values('Total Value', ascending=False)

# Main gallery visualisations
col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 Top 10 Galleries by Total Value")
    fig_top_galleries = go.Figure(data=[
        go.Bar(
            x=gallery_metrics['Total Value'].head(10).index,
            y=gallery_metrics['Total Value'].head(10),
            text=gallery_metrics['Total Value'].head(10).apply(lambda x: f'${x:,.0f}'),
            textposition='auto',
        )
    ])
    fig_top_galleries.update_layout(
        xaxis_title="Gallery",
        yaxis_title="Total Value ($)",
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_top_galleries, use_container_width=True)

with col2:
    st.subheader("📊 Works and Artists per Gallery")
    fig_works_artists = go.Figure(data=[
        go.Bar(
            name='Works',
            x=gallery_metrics['Number of Works'].head(10).index,
            y=gallery_metrics['Number of Works'].head(10),
            text=gallery_metrics['Number of Works'].head(10).apply(lambda x: f'{x:,.0f}'),
        ),
        go.Bar(
            name='Artists',
            x=gallery_metrics['Number of Artists'].head(10).index,
            y=gallery_metrics['Number of Artists'].head(10),
            text=gallery_metrics['Number of Artists'].head(10).apply(lambda x: f'{x:,.0f}'),
        )
    ])
    fig_works_artists.update_layout(
        barmode='group',
        xaxis_title="Gallery",
        yaxis_title="Quantity",
        height=400
    )
    st.plotly_chart(fig_works_artists, use_container_width=True)

# Gallery summary metrics
col3, col4, col5, col6 = st.columns(4)
with col3:
    st.metric("Average Works/Gallery", f"{gallery_metrics['Number of Works'].mean():.1f}")
with col4:
    st.metric("Average Artists/Gallery", f"{gallery_metrics['Number of Artists'].mean():.1f}")
with col5:
    st.metric("Average Value/Gallery", f"${gallery_metrics['Total Value'].mean():,.0f}")
with col6:
    st.metric("Average Works/Artist", f"{gallery_metrics['Works per Artist'].mean():.1f}")

# Scatter plot of Works vs Total Value relationship
st.subheader("📈 Relationship between Number of Works and Total Value")
fig_scatter = go.Figure(data=[
    go.Scatter(
        x=gallery_metrics['Number of Works'],
        y=gallery_metrics['Total Value'],
        mode='markers+text',
        text=gallery_metrics.index,
        textposition="top center",
        hovertemplate="<b>%{text}</b><br>" +
                      "Number of Works: %{x}<br>" +
                      "Total Value: $%{y:,.0f}<br>",
        marker=dict(
            size=10,
            color=gallery_metrics['Average Price'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Average Price ($)")
        )
    )
])
fig_scatter.update_layout(
    height=500,
    xaxis_title="Number of Works",
    yaxis_title="Total Value ($)",
)
st.plotly_chart(fig_scatter, use_container_width=True)

# Detailed table in expander
with st.expander("📋 View Complete Gallery Details"):
    st.dataframe(
        gallery_metrics.style.format({
            'Total Value': '${:,.2f}',
            'Average Price': '${:,.2f}',
            'Number of Works': '{:,.0f}',
            'Number of Artists': '{:,.0f}',
            'Works per Artist': '{:,.2f}'
        }),
        height=400
    )

# Artist Analysis
st.header("👨‍🎨 Artist Analysis")

# Prepare aggregated artist data
artist_metrics = df.groupby('Artist').agg({
    'Average Price': ['sum', 'mean', 'count'],
    'Gallery': 'nunique'
}).round(2)
artist_metrics.columns = ['Total Value', 'Average Price', 'Number of Works', 'Number of Galleries']
artist_metrics = artist_metrics.sort_values('Total Value', ascending=False)

# Artist summary metrics
col_a1, col_a2, col_a3, col_a4 = st.columns(4)
with col_a1:
    st.metric("Average Works/Artist", f"{artist_metrics['Number of Works'].mean():.1f}")
with col_a2:
    st.metric("Average Galleries/Artist", f"{artist_metrics['Number of Galleries'].mean():.1f}")
with col_a3:
    st.metric("Average Value/Artist", f"${artist_metrics['Total Value'].mean():,.0f}")
with col_a4:
    artists_exclusive = len(artist_metrics[artist_metrics['Number of Galleries'] == 1])
    st.metric("Exclusive Artists", f"{artists_exclusive:,}")

# Main artist visualisations
col_a5, col_a6 = st.columns(2)

with col_a5:
    st.subheader("💰 Top 10 Artists by Total Value")
    fig_top_artists = go.Figure(data=[
        go.Bar(
            x=artist_metrics['Total Value'].head(10).index,
            y=artist_metrics['Total Value'].head(10),
            text=artist_metrics['Total Value'].head(10).apply(lambda x: f'${x:,.0f}'),
            textposition='auto',
        )
    ])
    fig_top_artists.update_layout(
        xaxis_title="Artist",
        yaxis_title="Total Value ($)",
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_top_artists, use_container_width=True)

with col_a6:
    st.subheader("📊 Distribution of Works per Artist")
    fig_works_per_artist = go.Figure(data=[go.Histogram(
        x=artist_metrics['Number of Works'],
        nbinsx=20,
        name='Number of Artists',
        hovertemplate="Works: %{x}<br>Number of Artists: %{y}"
    )])
    fig_works_per_artist.update_layout(
        xaxis_title="Number of Works",
        yaxis_title="Number of Artists",
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_works_per_artist, use_container_width=True)

# Scatter plot of Works vs Total Value relationship for artists
st.subheader("📈 Relationship between Number of Works and Total Value per Artist")
fig_scatter_artist = go.Figure(data=[
    go.Scatter(
        x=artist_metrics['Number of Works'],
        y=artist_metrics['Total Value'],
        mode='markers',
        text=artist_metrics.index,
        hovertemplate="<b>%{text}</b><br>" +
                     "Number of Works: %{x}<br>" +
                     "Total Value: $%{y:,.0f}<br>" +
                     "Average Price: $%{marker.color:,.0f}<br>",
        marker=dict(
            size=10,
            color=artist_metrics['Average Price'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Average Price ($)")
        )
    )
])
fig_scatter_artist.update_layout(
    height=500,
    xaxis_title="Number of Works",
    yaxis_title="Total Value ($)",
)
st.plotly_chart(fig_scatter_artist, use_container_width=True)

# Artist diversification analysis
st.subheader("🎨 Artist Diversification by Galleries")
fig_diversification = go.Figure(data=[go.Histogram(
    x=artist_metrics['Number of Galleries'],
    nbinsx=10,
    name='Number of Artists',
    hovertemplate="Galleries: %{x}<br>Number of Artists: %{y}"
)])
fig_diversification.update_layout(
    xaxis_title="Number of Galleries Representing the Artist",
    yaxis_title="Number of Artists",
    showlegend=False,
    height=400
)
st.plotly_chart(fig_diversification, use_container_width=True)

# Detailed table of artists in expander
with st.expander("📋 View Complete Artist Details"):
    st.dataframe(
        artist_metrics.style.format({
            'Total Value': '${:,.2f}',
            'Average Price': '${:,.2f}',
            'Number of Works': '{:,.0f}',
            'Number of Galleries': '{:,.0f}'
        }),
        height=400
    )

# Time Trend Analysis
st.header("📅 Time Analysis")

# Prepare time data
df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
year_stats = df.groupby('Year').agg({
    'Average Price': ['mean', 'sum', 'count'],
    'Artist': 'nunique',
    'Gallery': 'nunique'
}).round(2)
year_stats.columns = ['Average Price', 'Total Value', 'Number of Works', 'Number of Artists', 'Number of Galleries']

# Time metrics
col_t1, col_t2, col_t3, col_t4 = st.columns(4)
with col_t1:
    growth_works = ((year_stats['Number of Works'].iloc[-1] / year_stats['Number of Works'].iloc[0]) - 1) * 100
    st.metric("Growth in Works", f"{growth_works:.1f}%")
with col_t2:
    growth_price = ((year_stats['Average Price'].iloc[-1] / year_stats['Average Price'].iloc[0]) - 1) * 100
    st.metric("Growth in Price", f"{growth_price:.1f}%")
with col_t3:
    growth_artists = ((year_stats['Number of Artists'].iloc[-1] / year_stats['Number of Artists'].iloc[0]) - 1) * 100
    st.metric("Growth in Artists", f"{growth_artists:.1f}%")
with col_t4:
    growth_galleries = ((year_stats['Number of Galleries'].iloc[-1] / year_stats['Number of Galleries'].iloc[0]) - 1) * 100
    st.metric("Growth in Galleries", f"{growth_galleries:.1f}%")

# Time visualisations
col_t5, col_t6 = st.columns(2)

with col_t5:
    st.subheader("📈 Price and Works Evolution")
    fig_temporal = go.Figure()
    
    # Add average price line
    fig_temporal.add_trace(
        go.Scatter(
            x=year_stats.index,
            y=year_stats['Average Price'],
            name='Average Price',
            line=dict(color='blue'),
            yaxis='y1'
        )
    )
    
    # Add works bar
    fig_temporal.add_trace(
        go.Bar(
            x=year_stats.index,
            y=year_stats['Number of Works'],
            name='Number of Works',
            yaxis='y2',
            marker_color='lightblue',
            opacity=0.7
        )
    )
    
    fig_temporal.update_layout(
        yaxis=dict(
            title="Average Price ($)",
            titlefont=dict(color="blue"),
            tickfont=dict(color="blue")
        ),
        yaxis2=dict(
            title="Number of Works",
            titlefont=dict(color="lightblue"),
            tickfont=dict(color="lightblue"),
            overlaying="y",
            side="right"
        ),
        xaxis_title="Year",
        hovermode='x unified',
        showlegend=True,
        height=400
    )
    st.plotly_chart(fig_temporal, use_container_width=True)

with col_t6:
    st.subheader("📊 Artist and Gallery Growth")
    fig_participants = go.Figure()
    
    # Add artist line
    fig_participants.add_trace(
        go.Scatter(
            x=year_stats.index,
            y=year_stats['Number of Artists'],
            name='Artists',
            line=dict(color='green'),
            mode='lines+markers'
        )
    )
    
    # Add gallery line
    fig_participants.add_trace(
        go.Scatter(
            x=year_stats.index,
            y=year_stats['Number of Galleries'],
            name='Galleries',
            line=dict(color='red'),
            mode='lines+markers'
        )
    )
    
    fig_participants.update_layout(
        yaxis_title="Number of Participants",
        xaxis_title="Year",
        hovermode='x unified',
        height=400
    )
    st.plotly_chart(fig_participants, use_container_width=True)

# Detailed time table in expander
with st.expander("📋 View Complete Details by Year"):
    st.dataframe(
        year_stats.style.format({
            'Average Price': '${:,.2f}',
            'Total Value': '${:,.2f}',
            'Number of Works': '{:,.0f}',
            'Number of Artists': '{:,.0f}',
            'Number of Galleries': '{:,.0f}'
        }),
        height=400
    )

# Market Analysis
st.header("🌎 Market Analysis")

# Prepare segmentation data
df['Price Segment'] = pd.qcut(
    df['Average Price'],
    q=4,
    labels=['Basic', 'Medium', 'Premium', 'Ultra Premium']
)

premium_threshold = df['Average Price'].quantile(0.9)
premium_works = df[df['Average Price'] > premium_threshold]

# First row - Segmentation Metrics
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    average_price_premium = premium_works['Average Price'].mean()
    st.metric("Average Price Premium", f"${average_price_premium:,.0f}")
with col_m2:
    obras_premium = len(premium_works)
    st.metric("Premium Works (Top 10%)", f"{obras_premium:,}")
with col_m3:
    value_premium = premium_works['Average Price'].sum()
    st.metric("Total Value Premium", f"${value_premium:,.0f}")
with col_m4:
    participation_premium = (value_premium / df['Average Price'].sum()) * 100
    st.metric("% Value Premium", f"{participation_premium:.1f}%")

# Second row - Segment Analysis
col_m5, col_m6 = st.columns(2)

with col_m5:
    st.subheader("📊 Distribution by Price Segment")
    segment_stats = df.groupby('Price Segment').agg({
        'Average Price': ['count', 'mean', 'sum']
    }).round(2)
    segment_stats.columns = ['Number of Works', 'Average Price', 'Total Value']
    
    # Calculate percentages
    segment_stats['% Works'] = (segment_stats['Number of Works'] / segment_stats['Number of Works'].sum()) * 100
    segment_stats['% Value'] = (segment_stats['Total Value'] / segment_stats['Total Value'].sum()) * 100
    
    fig_segments = go.Figure(data=[
        go.Bar(
            name='% Works',
            x=segment_stats.index,
            y=segment_stats['% Works'],
            text=segment_stats['% Works'].apply(lambda x: f'{x:.1f}%'),
            textposition='auto',
        ),
        go.Bar(
            name='% Value',
            x=segment_stats.index,
            y=segment_stats['% Value'],
            text=segment_stats['% Value'].apply(lambda x: f'{x:.1f}%'),
            textposition='auto',
        )
    ])
    
    fig_segments.update_layout(
        barmode='group',
        xaxis_title="Segment",
        yaxis_title="Percentage (%)",
        height=400
    )
    st.plotly_chart(fig_segments, use_container_width=True)

with col_m6:
    st.subheader("💰 Average Price by Segment")
    fig_price_segment = go.Figure(data=[
        go.Bar(
            x=segment_stats.index,
            y=segment_stats['Average Price'],
            text=segment_stats['Average Price'].apply(lambda x: f'${x:,.0f}'),
            textposition='auto',
        )
    ])
    
    fig_price_segment.update_layout(
        xaxis_title="Segment",
        yaxis_title="Average Price ($)",
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_price_segment, use_container_width=True)

# Regional Analysis if country column exists
if 'Country' in df.columns:
    st.subheader("🌍 Regional Analysis")
    
    # Prepare regional data
    region_stats = df.groupby('Country').agg({
        'Average Price': ['count', 'mean', 'sum'],
        'Artist': 'nunique',
        'Gallery': 'nunique'
    }).round(2)
    region_stats.columns = ['Number of Works', 'Average Price', 'Total Value', 'Number of Artists', 'Number of Galleries']
    
    col_m7, col_m8 = st.columns(2)
    
    with col_m7:
        st.subheader("📊 Participation by Country")
        region_stats['% Value'] = (region_stats['Total Value'] / region_stats['Total Value'].sum()) * 100
        
        fig_regions = go.Figure(data=[
            go.Pie(
                labels=region_stats.index,
                values=region_stats['Total Value'],
                textinfo='label+percent',
                hovertemplate="Country: %{label}<br>Total Value: $%{value:,.0f}<br>Percentage: %{percent}"
            )
        ])
        
        fig_regions.update_layout(height=400)
        st.plotly_chart(fig_regions, use_container_width=True)
    
    with col_m8:
        st.subheader("🎨 Average Price by Country")
        fig_price_country = go.Figure(data=[
            go.Bar(
                x=region_stats.index,
                y=region_stats['Average Price'],
                text=region_stats['Average Price'].apply(lambda x: f'${x:,.0f}'),
                textposition='auto',
            )
        ])
        
        fig_price_country.update_layout(
            xaxis_title="Country",
            yaxis_title="Average Price ($)",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_price_country, use_container_width=True)

# Artist Type Analysis if type column exists
if 'Artist Type' in df.columns:
    st.subheader("👨‍🎨 Artist Type Analysis")
    
    # Prepare type data
    artist_type_stats = df.groupby('Artist Type').agg({
        'Average Price': ['count', 'mean', 'sum'],
        'Artist': 'nunique'
    }).round(2)
    artist_type_stats.columns = ['Number of Works', 'Average Price', 'Total Value', 'Number of Artists']
    
    col_m9, col_m10 = st.columns(2)
    
    with col_m9:
        st.subheader("📊 Distribution by Artist Type")
        artist_type_stats['% Value'] = (artist_type_stats['Total Value'] / artist_type_stats['Total Value'].sum()) * 100
        
        fig_artist_type = go.Figure(data=[
            go.Pie(
                labels=artist_type_stats.index,
                values=artist_type_stats['Total Value'],
                textinfo='label+percent',
                hovertemplate="Type: %{label}<br>Total Value: $%{value:,.0f}<br>Percentage: %{percent}"
            )
        ])
        
        fig_artist_type.update_layout(height=400)
        st.plotly_chart(fig_artist_type, use_container_width=True)
    
    with col_m10:
        st.subheader("💰 Artist Type Metrics")
        st.dataframe(
            artist_type_stats.style.format({
                'Number of Works': '{:,.0f}',
                'Average Price': '${:,.2f}',
                'Total Value': '${:,.2f}',
                'Number of Artists': '{:,.0f}',
                '% Value': '{:.1f}%'
            }),
            height=400
        )

# Sales Status Analysis if status column exists
if 'Sales Status' in df.columns:
    st.subheader("📦 Sales Analysis")
    
    # Prepare sales data
    sales_stats = df.groupby('Sales Status').agg({
        'Average Price': ['count', 'mean', 'sum']
    }).round(2)
    sales_stats.columns = ['Number of Works', 'Average Price', 'Total Value']
    
    col_m11, col_m12 = st.columns(2)
    
    with col_m11:
        total_works = len(df)
        sold_works = len(df[df['Sales Status'] == 'Sold'])
        sales_rate = (sold_works / total_works) * 100
        
        fig_sales = go.Figure(data=[
            go.Pie(
                labels=['Sold', 'Not Sold'],
                values=[sold_works, total_works - sold_works],
                textinfo='label+percent',
                hole=.3
            )
        ])
        
        fig_sales.update_layout(
            title="Sales Status",
            height=400
        )
        st.plotly_chart(fig_sales, use_container_width=True)
    
    with col_m12:
        st.metric("Sales Rate", f"{sales_rate:.1f}%")
        st.metric("Sold Works", f"{sold_works:,}")
        st.metric("Total Sold Value", f"${sales_stats.loc['Sold', 'Total Value']:,.0f}")

# Detailed segment table in expander
with st.expander("📋 View Complete Details by Segment"):
    st.dataframe(
        segment_stats.style.format({
            'Number of Works': '{:,.0f}',
            'Average Price': '${:,.2f}',
            'Total Value': '${:,.2f}',
            '% Works': '{:.1f}%',
            '% Value': '{:.1f}%'
        }),
        height=400
    )

# Filtering and Filtered Data Section
st.header("🔍 Filtering and Detailed Data Exploration")
st.markdown("""
Use the following filters to explore data in detail. 
The filters will be applied to the data table below.
""")

# Container for filters
with st.container():
    # First row of filters
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        st.subheader("🏢 Gallery Filter")
        selected_gallery = st.multiselect(
            "Select Galleries",
            options=sorted(df['Gallery'].unique()),
            default=[]
        )
    
    with col_f2:
        st.subheader("💰 Price Range Filter")
        min_price = float(df['Average Price'].min())
        max_price = float(df['Average Price'].max())
        price_range = st.slider(
            "Select Price Range",
            min_value=min_price,
            max_value=max_price,
            value=(min_price, max_price),
            step=1000.0,  # Step of 1000 to avoid unnecessary decimals
            help="Slide to select price range"
        )
        st.caption(f"Selected range: ${price_range[0]:,.0f} - ${price_range[1]:,.0f}")
    
    with col_f3:
        st.subheader("📊 Segment Filter")
        selected_price_range = st.multiselect(
            "Select Price Segments",
            options=sorted(df['Price Segment'].unique()),
            default=[]
        )

    # Additional filters if columns exist
    col_f4, col_f5, col_f6 = st.columns(3)
    
    with col_f4:
        if 'Country' in df.columns:
            st.subheader("🌍 Country Filter")
            selected_country = st.multiselect(
                "Select Countries",
                options=sorted(df['Country'].unique()),
                default=[]
            )
    
    with col_f5:
        if 'Artist Type' in df.columns:
            st.subheader("👨‍🎨 Artist Type Filter")
            selected_artist_type = st.multiselect(
                "Select Artist Types",
                options=sorted(df['Artist Type'].unique()),
                default=[]
            )
    
    with col_f6:
        if 'Sales Status' in df.columns:
            st.subheader("📦 Sales Status Filter")
            selected_sale_status = st.multiselect(
                "Select Sales Status",
                options=sorted(df['Sales Status'].unique()),
                default=[]
            )

# Apply filters
mask = pd.Series(True, index=df.index)

if selected_gallery:
    mask &= df['Gallery'].isin(selected_gallery)

mask &= (df['Average Price'] >= price_range[0]) & (df['Average Price'] <= price_range[1])

if selected_price_range:
    mask &= df['Price Segment'].isin(selected_price_range)

if 'Country' in df.columns and selected_country:
    mask &= df['Country'].isin(selected_country)

if 'Artist Type' in df.columns and selected_artist_type:
    mask &= df['Artist Type'].isin(selected_artist_type)

if 'Sales Status' in df.columns and selected_sale_status:
    mask &= df['Sales Status'].isin(selected_sale_status)

df_filtered = df[mask]

# Show filter summary
st.subheader("📊 Filter Summary")
col_f7, col_f8, col_f9, col_f10 = st.columns(4)

with col_f7:
    st.metric("Selected Works", f"{len(df_filtered):,}")
with col_f8:
    st.metric("Selected Galleries", f"{df_filtered['Gallery'].nunique():,}")
with col_f9:
    st.metric("Selected Artists", f"{df_filtered['Artist'].nunique():,}")
with col_f10:
    filtered_value = df_filtered['Average Price'].sum()
    st.metric("Filtered Total Value", f"${filtered_value:,.0f}")

# Show filtered data
st.subheader("🎨 Filtered Works")
with st.expander("View Filtered Data", expanded=True):
    st.dataframe(
        df_filtered.style.format({
            'Minimum Price': '${:,.2f}',
            'Maximum Price': '${:,.2f}',
            'Average Price': '${:,.2f}'
        }),
        height=400
    ) 