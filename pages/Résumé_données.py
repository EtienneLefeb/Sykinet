import streamlit as st
import geopandas as gpd
import pandas as pd
from shapely import wkt
from st_files_connection import FilesConnection 
import matplotlib.pyplot as plt
from matplotlib.patches import Patch 
import numpy as np 

## 🌊 Application Cartographique d'Aléa d'Inondation et Sécheresse 🏠

# ***************************************************************
# 1. Configuration de la Page et Titre Principal
# ***************************************************************

# La configuration de la page peut être simplifiée ici car elle est définie dans la page principale,
# mais la garder assure que cette page a la bonne mise en page si elle est chargée seule.
st.set_page_config(
    page_title="Résumé des données climatiques",
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.title("Premières représentations ")
st.markdown("Visualisation des zones les plus touchées par l'aléa Sécheresse et l'aléa innondation")

conn = st.connection("gcs", type=FilesConnection) 
file_path = "streamlit-sykinet/base sykinet/df_secheresse_surface.csv"    
df = conn.read(file_path, input_format="csv")
df['geometry'] = df['geometry'].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:2154")

# Assurez-vous que la colonne NIVEAU est numérique pour le coloriage
gdf["NIVEAU"] = gdf["% surface NIVEAU = 3.0"] + gdf["% surface NIVEAU = 2.0"] / (gdf["% surface NIVEAU = 0.0"] + gdf["% surface NIVEAU = 1.0"] + gdf["% surface NIVEAU = 2.0"] +gdf["% surface NIVEAU = 3.0"])
# --- Création de la Carte avec Matplotlib et Geopandas ---

# 1. Créer la figure et l'axe Matplotlib
fig, ax = plt.subplots(1, 1, figsize=(12, 12))

# 2. Tracer le GeoDataFrame
# Nous utilisons la colonne 'NIVEAU' pour la couleur (choropleth map)
gdf.plot(
    column='NIVEAU', 
    ax=ax, 
    legend=True, # Afficher la légende
    cmap='viridis', # Carte de couleurs, vous pouvez choisir 'Reds', 'YlOrRd', etc.
    edgecolor='black',
    linewidth=0.5,
    legend_kwds={
        'label': "Part de zone à risqsue",
        'orientation': "horizontal",
        'shrink': 0.6,
        'pad': 0.01 # Réduire l'espacement
    }
)

# 3. Personnaliser la carte
ax.set_title("Carte des Zones d'Aléa par Niveau (0.0 à 3.0)", fontsize=18)
ax.set_axis_off() # Masquer les axes (latitude/longitude)

# 4. Afficher la carte dans Streamlit
st.pyplot(fig)