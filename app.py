import streamlit as st
import geopandas as gpd
from shapely import wkt
from st_files_connection import FilesConnection

st.title("Carte du Finistère")

# Créer la connexion GCS via Streamlit
conn = st.connection("gcs", type=FilesConnection)

# Lire ton CSV depuis le bucket GCS
df = conn.read("streamlit-sykinet/base sykinet/base_innondation.csv",
               input_format="csv",
               ttl=600)

# Convertir la colonne WKT en géométrie
df['geometry'] = df['geometry'].apply(wkt.loads)

# Créer GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

# Afficher la carte simple avec couleur par gridcode
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 8))
gdf.plot(column='gridcode', cmap='viridis', legend=True, ax=ax)
ax.set_axis_off()  # retire les axes pour une carte plus propre

st.pyplot(fig)
