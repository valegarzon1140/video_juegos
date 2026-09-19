import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard Ventas Videojuegos", page_icon="🎮", layout="wide")

# Título
st.title("🎮 Dashboard de Ventas de Videojuegos")

# Cargar datos
@st.cache_data
def load_data():
    file_path = "videojuegos_limpios.csv"  # Cambiado a CSV para mayor compatibilidad
    df = pd.read_csv(file_path)
    # Limpieza básica
    df = df.dropna(subset=['Año'])  # Eliminar filas sin año
    df['Año'] = df['Año'].astype(int)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error al cargar el archivo: {e}")
    st.stop()

# Sidebar - Filtros
st.sidebar.header("Filtros")

# Filtro Año
min_year = int(df['Año'].min())
max_year = int(df['Año'].max())
selected_years = st.sidebar.slider("Selecciona el rango de años", min_year, max_year, (min_year, max_year))

# Filtro Plataforma
all_platforms = df['Plataforma'].unique().tolist()
selected_platforms = st.sidebar.multiselect("Selecciona Plataforma(s)", all_platforms, default=all_platforms[:5])

# Filtro Género
all_genres = df['Genero'].unique().tolist()
selected_genres = st.sidebar.multiselect("Selecciona Género(s)", all_genres, default=all_genres)

# Aplicar filtros
df_filtered = df[
    (df['Año'] >= selected_years[0]) & 
    (df['Año'] <= selected_years[1]) &
    (df['Plataforma'].isin(selected_platforms)) &
    (df['Genero'].isin(selected_genres))
]
st.markdown("---")
region_seleccionada = st.sidebar.selectbox(
    "Región",
    ["Global", "Norteamérica", "Europa", "Japón", "Otros"]
)

columnas_region = {
    "Global": "Ventas Global",
    "Norteamérica": "Ventas NA",
    "Europa": "Ventas EU",
    "Japón": "Ventas JP",
    "Otros": "Ventas Otros"
}

columna_ventas = columnas_region[region_seleccionada]

if df_filtered.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()


# KPIs
# Filtrar solamente juegos con ventas en la región seleccionada
df_region = df_filtered[
    df_filtered[columna_ventas] > 0
]

# KPIs
col1, col2, col3, col4 = st.columns(4)

# Ventas totales de la región seleccionada
total_sales = df_region[columna_ventas].sum()

# Juego más vendido en la región seleccionada
top_game = df_region.loc[
    df_region[columna_ventas].idxmax(),
    "Nombre"
]

# Editorial con mayores ventas en la región seleccionada
top_publisher = (
    df_region
    .groupby("Editorial")[columna_ventas]
    .sum()
    .idxmax()
)

# Cantidad de juegos que tuvieron ventas en esa región
total_games = len(df_region)

# Mostrar KPIs
col1.metric(
    f"Ventas Totales - {region_seleccionada}",
    f"{total_sales:,.2f} M"
)

col2.metric(
    "Juego Más Vendido",
    top_game
)

col3.metric(
    "Editorial Top",
    top_publisher
)

col4.metric(
    f"Juegos con ventas - {region_seleccionada}",
    total_games
)


# Gráficos
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Ventas Globales por Año")
    sales_by_year = df_filtered.groupby('Año')['Ventas Global'].sum().reset_index()
    fig_year = px.bar(sales_by_year, x='Año', y='Ventas Global', title="Ventas por Año", color_discrete_sequence=['#4C78A8'])
    st.plotly_chart(fig_year, use_container_width=True)

with col_right:
    st.subheader("Ventas Globales por Género")
    sales_by_genre = df_filtered.groupby('Genero')['Ventas Global'].sum().reset_index()
    fig_genre = px.pie(sales_by_genre, values='Ventas Global', names='Genero', title="Distribución por Género", hole=0.4)
    st.plotly_chart(fig_genre, use_container_width=True)

st.subheader("Top 10 Juegos por Ventas Globales")
top_10_games = df_filtered.nlargest(10, 'Ventas Global')
fig_top10 = px.bar(top_10_games, x='Ventas Global', y='Nombre', orientation='h', title="Top 10 Juegos", color='Ventas Global', color_continuous_scale='Viridis')
fig_top10.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_top10, use_container_width=True)

# Gráfico de ventas totales por región
st.subheader("🌎 Ventas Totales por Región")

ventas_region = pd.DataFrame({
    "Región": ["Norteamérica", "Europa", "Japón", "Otros"],
    "Ventas": [
        df_filtered["Ventas NA"].sum(),
        df_filtered["Ventas EU"].sum(),
        df_filtered["Ventas JP"].sum(),
        df_filtered["Ventas Otros"].sum()
    ]
})

fig_region = px.bar(
    ventas_region,
    x="Región",
    y="Ventas",
    title="Ventas Totales por Región",
    text_auto=".2f"
)

fig_region.update_layout(
    xaxis_title="Región",
    yaxis_title="Ventas (millones de unidades)"
)

st.plotly_chart(
    fig_region,
    use_container_width=True
)

st.markdown("---")
st.subheader("Datos Detallados")
st.dataframe(df_filtered)
# para ejecutar el script, asegúrense de tener instalado Streamlit y Plotly, y ejecuta el siguiente comando en la terminal:
# streamlit run dashboard.py
# Asegurece de tener el archivo "Ventas Videojuegos.xlsx" en el mismo directorio que este script para que funcione correctamente.
# Ventas totales por región

