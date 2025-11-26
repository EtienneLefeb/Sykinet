import streamlit as st
from st_files_connection import FilesConnection
import geopandas as gpd
from shapely import wkt
import folium
from streamlit_folium import st_folium

st.title("Carte du Finistère")

# Récupérer le secret
gcs_token = st.secrets["gcs"]["token"]

# Connexion à GCS
conn = st.connection("gcs", type=FilesConnection, token=gcs_token)

# Lire le CSV
df = conn.read("streamlit-sykinet/base sykinet/base_innondation.csv",
               input_format="csv", ttl=600)

# Transformer en GeoDataFrame
df['geometry'] = df['geom'].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

# Afficher la carte
m = folium.Map(location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom_start=10)
folium.GeoJson(gdf).add_to(m)
st_folium(m, width=700, height=500)

