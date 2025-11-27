import streamlit as st
import geopandas as gpd
from shapely import wkt
from st_files_connection import FilesConnection 
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch # <-- NOUVEL IMPORT

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

# Définition du mapping (valeur : [couleur, label])
legend_mapping = {
    0: ['green', "0 : Pas de débordement de nappe ni d'inondation de cave"],
    1: ['yellow', "1 : Zones potentiellement sujettes aux débordements de nappe"],
    2: ['blue', "2 : Zones potentiellement sujettes aux inondations de cave"]
}

minx, miny, maxx, maxy = gdf_projete.total_bounds

# --- Configuration Matplotlib ---
fig, ax = plt.subplots(figsize=(10, 10))

# Définition explicite des limites des axes
x_buffer = (maxx - minx) * 0.02
y_buffer = (maxy - miny) * 0.02
ax.set_xlim(minx - x_buffer, maxx + x_buffer)
ax.set_ylim(miny - y_buffer, maxy + y_buffer)
ax.set_aspect('equal')
ax.set_axis_off()

ax.set_title("Carte d'Aléa Basée sur le Gridcode", fontsize=16)

# ***************************************************************
# MODIFICATION CLÉ : Préparer les handles de légende avec des Patch simples
# ***************************************************************

legend_handles = [] # Pour stocker les objets Patch
legend_labels = []  # Pour stocker les labels

# Itération sur les classes numériques (0, 1, 2)
for code, (color, label) in legend_mapping.items():
    # 1. Filtrez le GeoDataFrame pour le code actuel
    subset = gdf_projete[gdf_projete['gridcode'] == code]
    
    if not subset.empty:
        # 2. Tracez le sous-ensemble avec une couleur fixe
        # Pas besoin de stocker l'objet retourné par plot() ici
        subset.plot(
            ax=ax,
            color=color,
            edgecolor='white', 
            linewidth=0.1,
            # Supprimez le 'label' ici, nous le gérons manuellement
            # label=label 
        )
        
        # 3. Créez un objet Patch (un simple carré) pour la légende
        legend_handles.append(Patch(color=color, label=label))
        legend_labels.append(label)

# ***************************************************************
# Créer la légende discrète en utilisant les Patch simples
# ***************************************************************

ax.legend(
    handles=legend_handles, # On passe nos objets Patch créés explicitement
    labels=legend_labels,   # On passe nos labels
    title="Grille de Code d'Aléa",
    loc='lower right', 
    fancybox=True, 
    framealpha=0.8,
    borderpad=1 
)
st.pyplot(fig)