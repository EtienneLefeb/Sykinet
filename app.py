import streamlit as st
import geopandas as gpd
from shapely import wkt
from st_files_connection import FilesConnection 
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

st.title("Carte du département")
# st.set_page_config() # À mettre en haut du script

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

# ***************************************************************
# CORRECTION CRITIQUE : Assurer que la colonne 'gridcode' est numérique
# ***************************************************************
if gdf_projete['gridcode'].dtype != 'int64':
    try:
        gdf_projete['gridcode'] = gdf_projete['gridcode'].astype(int)
    except Exception as e:
        st.error(f"Erreur lors de la conversion de 'gridcode' en entier : {e}")
        st.stop()


minx, miny, maxx, maxy = gdf_projete.total_bounds

# --- Configuration Matplotlib et Colormap ---
fig, ax = plt.subplots(figsize=(10, 10))

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

# Définition explicite des limites des axes
x_buffer = (maxx - minx) * 0.02
y_buffer = (maxy - miny) * 0.02
ax.set_xlim(minx - x_buffer, maxx + x_buffer)
ax.set_ylim(miny - y_buffer, maxy + y_buffer)

# --- Tracé et Affichage ---
ax.set_aspect('equal')
ax.set_axis_off()

# Tracé de la carte : legend=False pour gérer la colorbar manuellement
mappable = gdf_projete.plot(
    column='gridcode',
    ax=ax,
    cmap=cmap,
    norm=norm,
    legend=False, # Désactive la création automatique problématique
)

ax.set_title("Carte d'Aléa Basée sur le Gridcode", fontsize=16)

# ***************************************************************
# CRÉATION MANUELLE ET FIABLE DE LA COLORBAR
# ***************************************************************

# Création de la colorbar à partir du mappable
cbar = fig.colorbar(
    mappable, 
    ax=ax, 
    orientation="horizontal",
    shrink=0.7, 
    aspect=30,
    drawedges=True,
    extend='neither',
    ticks=ticks, # Utilisation des ticks numériques
    label="Grille de Code d'Aléa (Gridcode)"
)

# Application des labels personnalisés aux ticks
cbar.set_ticklabels(legend_labels)

st.pyplot(fig)