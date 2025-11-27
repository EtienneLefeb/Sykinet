import streamlit as st
import geopandas as gpd
from shapely import wkt
from st_files_connection import FilesConnection 
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

st.title("Carte du département")

dep = [f"{i:02d}" for i in range(1, 96) if i != 20]
dep.insert(19, "2A") 
dep.insert(20, "2B") 

departement = st.selectbox("departement",dep)
# --- Connexion et Chargement des Données ---
conn = st.connection("gcs", type=FilesConnection)
# Le reste de votre logique de chargement...
df = conn.read("streamlit-sykinet/base sykinet/base_innondation"+departement+".csv",
                input_format="csv",
                ttl=600)
df['geometry'] = df['geometry'].apply(wkt.loads)
gdf_projete = gpd.GeoDataFrame(df, geometry='geometry',crs="EPSG:2154")

minx, miny, maxx, maxy = gdf_projete.total_bounds

# --- Configuration de la figure Matplotlib ---
fig, ax = plt.subplots(figsize=(10, 10))

# --- Définition des couleurs, normalisation et ticks ---
colors = ['green', 'yellow', 'blue']
legend_labels = [
    "0 : Pas de débordement de nappe ni d'inondation de cave",
    "1 : Zones potentiellement sujettes aux débordements de nappe",
    "2 : Zones potentiellement sujettes aux inondations de cave"
]
ticks = [0, 1, 2] 

cmap = ListedColormap(colors)
boundaries = [-0.5, 0.5, 1.5, 2.5]
norm = BoundaryNorm(boundaries, cmap.N)

# Configuration de la colorbar (colorbar_kwds)
colorbar_kwds = {
    'orientation': "horizontal",
    'shrink': 0.7, 
    'aspect': 30,
    'label': "Grille de Code d'Aléa (Gridcode)",
    'ticks': ticks,
    'drawedges': True,
    'extend': 'neither'
}

# Définition explicite des limites des axes
x_buffer = (maxx - minx) * 0.02
y_buffer = (maxy - miny) * 0.02
ax.set_xlim(minx - x_buffer, maxx + x_buffer)
ax.set_ylim(miny - y_buffer, maxy + y_buffer)

# --- Tracé et Affichage ---
ax.set_aspect('equal')
ax.set_axis_off()
# CODE CORRIGÉ pour le tracé et la personnalisation
# ... (votre code jusqu'à la ligne ci-dessous)

# Tracé de la carte : Stocker le mappable retourné
mappable = gdf_projete.plot(
    column='gridcode',
    ax=ax,
    cmap=cmap,
    norm=norm,
    legend=False, # <-- IMPORTANT : On crée la colorbar manuellement
    # colorbar_kwds=colorbar_kwds # <-- On pourrait le laisser, mais on simplifie
)

ax.set_title("Carte d'Aléa Basée sur le Gridcode", fontsize=16)

# ***************************************************************
# ÉTAPE ULTRA-FIABLE : Créer et personnaliser la colorbar explicitement
# ***************************************************************

# Création de la colorbar à partir du mappable
# On passe les kwds ici si on les a retirés ci-dessus
cbar = fig.colorbar(
    mappable, 
    ax=ax, 
    orientation="horizontal",
    shrink=0.7, 
    aspect=30,
    drawedges=True,
    extend='neither',
    ticks=ticks # On passe les ticks ici
)

# Application des labels personnalisés
cbar.set_ticklabels(legend_labels)

st.pyplot(fig)