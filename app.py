import streamlit as st
from st_files_connection import FilesConnection
import geopandas as gpd

st.title("Carte du Finistère")
gdf = gpd.read_file(
    "streamlit-sykinet://base sykinet/Dept_29.zip!VECTEUR",
    storage_options={"token": "C:/Users/lefeb/OneDrive/Documents/Sykinet/base sykinet/sound-bee-479419-k3-89105ea1b821.json"}
)
if gdf.crs != "EPSG:4326":
    gdf = gdf.to_crs("EPSG:4326")

st.map(gdf)
