import streamlit as st
import geopandas as gpd
from shapely import wkt
from st_files_connection import FilesConnection
import matplotlib.pyplot as plt

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

fig, ax = plt.subplots(figsize=(6, 6))
ax.set_aspect(1)
ax.set_axis_off()  # retire les axes pour une carte plus propre

gdf.plot(column='gridcode', cmap='viridis', legend=True, ax=ax)

st.pyplot(fig)
