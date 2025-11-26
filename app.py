import streamlit as st
import geopandas as gpd
from shapely import wkt
from st_files_connection import FilesConnection
import matplotlib.pyplot as plt
from io import BytesIO

st.title("Carte du Finistère")
st.set_page_config(layout='wide')
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
gdf_projete = gdf.to_crs(epsg=2154) # 2154 est le code pour Lambert 93

# Afficher la carte simple avec couleur par gridcode
width = st.sidebar.slider("plot width", 1, 25, 3)
height = st.sidebar.slider("plot height", 1, 25, 1)

fig, ax = plt.subplots(figsize=(width, height))
ax.set_aspect('equal')
ax.set_axis_off()  # retire les axes pour une carte plus propre
gdf_projete.plot(column='gridcode', cmap='viridis', legend=False, ax=ax)

st.pyplot(fig)
