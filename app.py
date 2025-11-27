import streamlit as st
import geopandas as gpd
from shapely import wkt
from st_files_connection import FilesConnection
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

st.title("Carte du département")
st.set_page_config()

dep = [f"{i:02d}" for i in range(1, 96) if i != 20]
dep.insert(19, "2A")  # après "19"
dep.insert(20, "2B")  # après "2A"

departement = st.selectbox("departement",dep)
# --- Connexion et Chargement des Données (Identique) ---
conn = st.connection("gcs", type=FilesConnection)
df = conn.read("streamlit-sykinet/base sykinet/base_innondation"+departement+".csv",
               input_format="csv",
               ttl=600)
df['geometry'] = df['geometry'].apply(wkt.loads)
gdf_projete = gpd.GeoDataFrame(df, geometry='geometry',crs="EPSG:2154")

# ***************************************************************
# ÉTAPE CLÉ 1 : Calculer les limites (bounds) de la géométrie projetée
# ***************************************************************
minx, miny, maxx, maxy = gdf_projete.total_bounds

# --- Configuration de la figure Matplotlib ---
# Nous utilisons toujours cette méthode pour garantir le bon aspect ratio,
# et nous n'utilisons pas les sliders pour figsize (pour éviter la déformation initiale).
fig, ax = plt.subplots(figsize=(5, 5))
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

legend_kwds = {
    'orientation': "horizontal",
    'shrink': 0.5, # Ajustez la taille de la barre de couleur
    'aspect': 30,  # Ajustez le rapport hauteur/largeur de la barre de couleur
    'label': "Grille de Code d'Aléa (Gridcode)",
    'ticks': ticks,
    'labels': legend_labels,
    'drawedges': True # Utile pour bien voir les limites entre les classes
}
# ***************************************************************
# ÉTAPE CLÉ 2 : Définir explicitement les limites des axes (xlim, ylim)
# ***************************************************************
# Ajout d'une petite marge (buffer) pour que la carte ne touche pas les bords
x_buffer = (maxx - minx) * 0.02
y_buffer = (maxy - miny) * 0.02

ax.set_xlim(minx - x_buffer, maxx + x_buffer)
ax.set_ylim(miny - y_buffer, maxy + y_buffer)

gdf_projete["gridcode"] = str(gdf_projete["gridcode"])
# --- Tracé et Affichage ---
ax.set_aspect('equal') # Garantit le bon rapport d'aspect
ax.set_axis_off()
gdf_projete.plot(
    column='gridcode',
    ax=ax,
    cmap=cmap,           # Utilisation de la carte de couleurs personnalisée
    norm=norm,           # Utilisation de la normalisation personnalisée
    legend=True,
    legend_kwds=legend_kwds
)

ax.set_title("Carte d'Aléa Basée sur le Gridcode", fontsize=16)
# Optionnel : Sliders pour ajuster la taille du conteneur Streamlit (non la taille interne de la figure)
#plot_width = st.sidebar.slider("Largeur de la carte (pixels)", 100, 1000, 500)
#plot_height = st.sidebar.slider("Hauteur de la carte (pixels)", 100, 1000, 700) 

st.pyplot(fig)