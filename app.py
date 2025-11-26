import streamlit as st
from st_files_connection import FilesConnection
import pandas as pd
import geopandas as gpd
from shapely import wkt

st.title("Carte du Finistère")

# Créer la connexion GCS via Streamlit
conn = st.connection("gcs", type=FilesConnection)

# Lire ton CSV depuis le bucket GCS
df = conn.read("streamlit-sykinet/base sykinet/base_innondation.csv",
               input_format="csv",
               ttl=600)

# Convertir la colonne WKT en géométrie
df['geometry'] = df['geometry'].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

# Afficher sur la carte
st.map(gdf)
