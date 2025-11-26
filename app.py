import streamlit as st
from st_files_connection import FilesConnection
import pandas as pd
import geopandas as gpd
from shapely import wkt
import folium
from streamlit_folium import st_folium

st.title("Carte du Finistère")

# Connexion GCS via Streamlit
conn = st.connection("gcs", type=FilesConnection)

# Lire le CSV depuis le bucket GCS
df = conn.read("streamlit-sykinet/base sykinet/base_innondation.csv",
               input_format="csv",
               ttl=600)

# Convertir la colonne WKT en géométrie
df['geometry'] = df['geometry'].apply(wkt.loads)

# Créer GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

# Créer la carte centrée sur le Finistère
m = folium.Map(location=[48.0, -4.0], zoom_start=9)

# Couleurs fixes pour gridcode
color_dict = {
    0: '#1f77b4',  # bleu
    1: '#ff7f0e',  # orange
    2: '#2ca02c',  # vert
}

# Ajouter les polygones avec couleur selon gridcode
for _, row in gdf.iterrows():
    sim_geo = gpd.GeoSeries([row['geometry']]).__geo_interface__
    folium.GeoJson(
        sim_geo,
        style_function=lambda x, grid=row['gridcode']: {
            'fillColor': color_dict.get(grid, '#gray'),
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.6
        },
        tooltip=folium.Tooltip(f"gridcode: {row['gridcode']}<br>Classe: {row['CLASSE']}")
    ).add_to(m)

# Afficher la carte interactive
st_data = st_folium(m, width=700, height=500)
