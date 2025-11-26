import streamlit as st
from st_files_connection import FilesConnection
import pandas as pd
import geopandas as gpd
from shapely import wkt
import folium
from streamlit_folium import st_folium
import pydeck as pdk

st.title("Carte du Finistère")

# Connexion GCS via Streamlit
conn = st.connection("gcs", type=FilesConnection)

# Lire le CSV depuis le bucket GCS
df = conn.read("streamlit-sykinet/base sykinet/base_innondation.csv",
               input_format="csv",
               ttl=600) 

# Convertir la colonne WKT en géométrie
df['geometry'] = df['geometry'].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

# Extraire latitude et longitude
gdf['lon'] = gdf.geometry.x
gdf['lat'] = gdf.geometry.y

# Couleurs par gridcode
color_map = {0: [0,0,255], 1: [0,255,0], 2: [255,0,0]}  # bleu, vert, rouge
gdf['color'] = gdf['gridcode'].map(color_map)

# Pydeck chart
layer = pdk.Layer(
    "ScatterplotLayer",
    data=gdf,
    get_position='[lon, lat]',
    get_fill_color='color',
    get_radius=50,
    pickable=True
)

view_state = pdk.ViewState(
    longitude=gdf['lon'].mean(),
    latitude=gdf['lat'].mean(),
    zoom=9
)

st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))
