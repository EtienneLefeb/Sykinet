import streamlit as st
import geopandas as gpd
from shapely import wkt
from st_files_connection import FilesConnection
import matplotlib.pyplot as plt
# import numpy as np # non nécessaire
# from io import BytesIO # non nécessaire

st.title("Carte du Finistère")
# st.set_page_config(layout='wide') # Ceci est OK

# --- Connexion et Chargement des Données ---
conn = st.connection("gcs", type=FilesConnection)
df = conn.read("streamlit-sykinet/base sykinet/base_innondation.csv",
               input_format="csv",
               ttl=600)

# Conversion WKT et GeoDataFrame
df['geometry'] = df['geometry'].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

# Projection en Lambert 93 (EPSG:2154) - Maintient la forme
gdf_projete = gdf.to_crs(epsg=2154)

# --- Configuration de la figure Matplotlib ---

# 1. Option : Utilisez une taille de figure fixe et raisonnable.
# Le Finistère est beaucoup plus long que large (ratio ~3:1 ou 4:1).
# fig, ax = plt.subplots(figsize=(6, 16)) # Exemple d'un bon rapport pour le Finistère

# 2. Recommandé : Laissez Matplotlib calculer la taille en fonction du rapport d'aspect.
# Ne pas spécifier de figsize permet à Matplotlib de choisir une taille par défaut.
fig, ax = plt.subplots() # Pas de figsize spécifié ici

# ******************************************************************
# LIGNE CRUCIALE : MAINTENIR LE RAPPORT D'ASPECT DES COORDONNÉES
# 'equal' combiné à 'adjustable="box"' assure que les axes sont mis
# à l'échelle correctement pour correspondre aux données géographiques.
# ******************************************************************
ax.set_aspect('equal', adjustable='box')
ax.set_axis_off() 

# Tracé de la carte
gdf.plot(column='gridcode', cmap='viridis', legend=False, ax=ax)

# Pour s'assurer que les sliders Streamlit impactent l'affichage final,
# nous pouvons les utiliser pour **ajuster la taille d'affichage** de la figure
# mais PAS sa taille interne (figsize), qui déformerait l'image.

plot_width = st.sidebar.slider("Largeur de la carte (pixels)", 100, 1000, 500)
plot_height = st.sidebar.slider("Hauteur de la carte (pixels)", 100, 1000, 700) # Ajuster le défaut

# Affichage Streamlit avec les dimensions ajustées par les sliders
st.pyplot(fig, use_container_width=False, clear_figure=True)
# Si vous souhaitez une largeur adaptative (et laisser Streamlit gérer l'aspect ratio
# du conteneur), vous pouvez utiliser :
# st.pyplot(fig, use_container_width=True)