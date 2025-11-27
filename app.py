import streamlit as st
import geopandas as gpd
from shapely import wkt
# Assurez-vous d'avoir st_files_connection installé si vous utilisez GCS
from st_files_connection import FilesConnection 
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

st.title("Carte du département")
# La configuration doit être faite avant la première commande Streamlit, 
# mais 'st.title' est déjà appelé. En pratique, placez-le avant 'st.title'.
# st.set_page_config() 

dep = [f"{i:02d}" for i in range(1, 96) if i != 20]
dep.insert(19, "2A") 
dep.insert(20, "2B") 

departement = st.selectbox("departement",dep)
# --- Connexion et Chargement des Données ---
conn = st.connection("gcs", type=FilesConnection)
df = conn.read("streamlit-sykinet/base sykinet/base_innondation"+departement+".csv",
                input_format="csv",
                ttl=600)
df['geometry'] = df['geometry'].apply(wkt.loads)
gdf_projete = gpd.GeoDataFrame(df, geometry='geometry',crs="EPSG:2154")

# ÉTAPE CLÉ 1 : Calculer les limites (bounds) de la géométrie projetée
minx, miny, maxx, maxy = gdf_projete.total_bounds

# --- Configuration de la figure Matplotlib ---
fig, ax = plt.subplots(figsize=(10, 10)) # Augmentation de la taille pour meilleure visibilité

# --- Définition des couleurs, normalisation et ticks ---
colors = ['green', 'yellow', 'blue']
legend_labels = [
    "0 : Pas de débordement de nappe ni d'inondation de cave",
    "1 : Zones potentiellement sujettes aux débordements de nappe",
    "2 : Zones potentiellement sujettes aux inondations de cave"
]
ticks = [0, 1, 2] # Les centres des classes pour la colorbar

cmap = ListedColormap(colors)
boundaries = [-0.5, 0.5, 1.5, 2.5]
norm = BoundaryNorm(boundaries, cmap.N)

# *** CORRECTION MAJEURE: Utiliser colorbar_kwds ***
colorbar_kwds = {
    'orientation': "horizontal",
    'shrink': 0.7, 
    'aspect': 30,
    'label': "Grille de Code d'Aléa (Gridcode)",
    'ticks': ticks,
    'drawedges': True,
    'extend': 'neither'
}

# ÉTAPE CLÉ 2 : Définir explicitement les limites des axes (xlim, ylim)
x_buffer = (maxx - minx) * 0.02
y_buffer = (maxy - miny) * 0.02
ax.set_xlim(minx - x_buffer, maxx + x_buffer)
ax.set_ylim(miny - y_buffer, maxy + y_buffer)

# Le gridcode doit être numérique pour la normalisation!
# Si vous le convertissez en string, la normalisation ne fonctionnera pas correctement.
# Rejetez cette ligne: gdf_projete["gridcode"] = str(gdf_projete["gridcode"]) 

# --- Tracé et Affichage ---
ax.set_aspect('equal')
ax.set_axis_off()

# Tracé de la carte
# La fonction plot renvoie un objet mappable (ici, un polycollection)
mappable = gdf_projete.plot(
    column='gridcode',
    ax=ax,
    cmap=cmap,
    norm=norm,
    legend=True,
    colorbar_kwds=colorbar_kwds # <-- Utilisation de colorbar_kwds corrigée
)

ax.set_title("Carte d'Aléa Basée sur le Gridcode", fontsize=16)

# *** ÉTAPE 4 : Personnaliser les étiquettes (labels) de la colorbar ***
# On récupère la colorbar générée par GeoPandas/Matplotlib
cbar = fig.axes[1] # La colorbar est souvent le deuxième axe créé (index 1)

# On applique les étiquettes personnalisées à la colorbar
cbar.set_xticklabels(legend_labels)

st.pyplot(fig)