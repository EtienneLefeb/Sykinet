import streamlit as st
from st_files_connection import FilesConnection
import pandas as pd
import geopandas as gpd
from shapely import wkt
import folium
from streamlit_folium import st_folium

st.title("Carte du Finistère")

# Créer la connexion GCS via Streamlit
conn = st.connection("gcs", type=FilesConnection)

# Lire le CSV depuis le bucket GCS
df = conn.read("streamlit-sykinet/base sykinet/base_innondation.csv",
               input_format="csv",
               ttl=600)

# Convertir la colonne WKT en géométrie
df['geometry'] = df['geometry'].apply(wkt.loads)

# Créer le GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

# Centrer la carte sur le Finistère (approx.)
m = folium.Map(location=[48.0, -4.0], zoom_start=8)

# Ajouter les géométries
folium.GeoJson(gdf).add_to(m)

# Afficher la carte dans Streamlit
st_folium(m, width=700, height=500)
