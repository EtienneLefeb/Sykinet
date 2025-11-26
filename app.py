import streamlit as st
import geopandas as gpd
from shapely import wkt
from st_files_connection import FilesConnection
import matplotlib.pyplot as plt

st.title("Carte du Finistère")
st.set_page_config(layout='wide')

# --- Connexion et Chargement des Données (Identique) ---
conn = st.connection("gcs", type=FilesConnection)
df = conn.read("streamlit-sykinet/base sykinet/base_innondation.csv",
               input_format="csv",
               ttl=600)
df['geometry'] = df['geometry'].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

# --- Projection en Lambert 93 (Identique) ---
gdf_projete = gdf.to_crs(epsg=2154)

# ***************************************************************
# ÉTAPE CLÉ 1 : Calculer les limites (bounds) de la géométrie projetée
# ***************************************************************
minx, miny, maxx, maxy = gdf_projete.total_bounds

# --- Configuration de la figure Matplotlib ---
# Nous utilisons toujours cette méthode pour garantir le bon aspect ratio,
# et nous n'utilisons pas les sliders pour figsize (pour éviter la déformation initiale).
fig, ax = plt.subplots()

# ***************************************************************
# ÉTAPE CLÉ 2 : Définir explicitement les limites des axes (xlim, ylim)
# ***************************************************************
# Ajout d'une petite marge (buffer) pour que la carte ne touche pas les bords
x_buffer = (maxx - minx) * 0.02
y_buffer = (maxy - miny) * 0.02

ax.set_xlim(minx - x_buffer, maxx + x_buffer)
ax.set_ylim(miny - y_buffer, maxy + y_buffer)


# --- Tracé et Affichage ---
ax.set_aspect('equal', adjustable='box') # Garantit le bon rapport d'aspect
ax.set_axis_off()
gdf_projete.plot(column='gridcode', cmap='viridis', legend=False, ax=ax)

# Optionnel : Sliders pour ajuster la taille du conteneur Streamlit (non la taille interne de la figure)
#plot_width = st.sidebar.slider("Largeur de la carte (pixels)", 100, 1000, 500)
#plot_height = st.sidebar.slider("Hauteur de la carte (pixels)", 100, 1000, 700) 

st.pyplot(fig)