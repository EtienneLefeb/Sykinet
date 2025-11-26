import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from shapely import wkt
from st_files_connection import FilesConnection

st.title("Carte du Finistère")

# Chemin vers le fichier GCS
conn = st.connection('gcs', type=FilesConnection)

df = conn.read(" streamlit-sykinet/base sykinet/base_innondation.csv", input_format="csv", ttl=600)

df['geometry'] = df['geom'].apply(wkt.loads)

gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

st.map(gdf)


