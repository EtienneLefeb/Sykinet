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
width = st.sidebar.slider("plot width", 1, 25, 3)
height = st.sidebar.slider("plot height", 1, 25, 1)

fig, ax = plt.subplots(figsize=(width, height))
ax.set_axis_off()  # retire les axes pour une carte plus propre

gdf.plot(column='gridcode', cmap='viridis', legend=True, ax=ax)

buf = BytesIO()
fig.savefig(buf, format="png")
st.image(buf)
