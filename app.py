import streamlit as st
import geopandas as gpd
import pandas as pd
from shapely import wkt
from st_files_connection import FilesConnection 
import matplotlib.pyplot as plt
from matplotlib.patches import Patch 
import numpy as np # Import pour la gestion des données

## 🌊 Application Cartographique d'Aléa d'Inondation 🏠

# ***************************************************************
# 1. Configuration de la Page et Titre Principal
# ***************************************************************

# Configuration de la page doit être la première commande Streamlit
st.set_page_config(
    page_title="Carte d'Aléa d'Inondation",
    layout="wide", # Utiliser toute la largeur de l'écran
    initial_sidebar_state="expanded"
)

st.title("🗺️ Carte d'Aléa du Département")
st.markdown("Visualisation des zones potentiellement sujettes aux débordements de nappe ou aux inondations de cave.")

# ***************************************************************
# 2. Sélecteur de Département dans la Barre Latérale (st.sidebar)
# ***************************************************************

with st.sidebar:
    st.header("Paramètres de la Carte")
    
    # Liste des départements français (inclut 2A/2B pour la Corse)
    dep = [f"{i:02d}" for i in range(1, 96) if i != 20]
    dep.insert(19, "2A") 
    dep.insert(20, "2B") 
    
    # Utilisation d'un cache pour éviter de recalculer la liste à chaque interaction
    @st.cache_data
    def get_department_list():
        return dep
        
    departement = st.selectbox(
        "Sélectionnez le Département",
        get_department_list(),
        index=30, # Ex: commence sur le 31
        help="Le code départemental (ex: 75 pour Paris)."
    )
    
    # Afficher le département sélectionné pour confirmation
    st.info(f"Département sélectionné : **{departement}**")

# ***************************************************************
# 3. Chargement et Préparation des Données
# ***************************************************************

# Utiliser st.cache_data pour mettre en cache le GeoDataFrame après le chargement et la conversion
@st.cache_data(ttl=600)
def load_and_prepare_data(dept_code):
    try:
        # Connexion et Chargement des Données
        conn = st.connection("gcs", type=FilesConnection)
        file_path = f"streamlit-sykinet/base sykinet/base_innondation{dept_code}.csv"
        file_path2 = f"streamlit-sykinet/base sykinet/df_secheresse{dept_code}.csv"
        # Le widget de statut s'affiche automatiquement avec st.cache_data
        df = conn.read(file_path, input_format="csv")
        
        # Conversion WKT en géométrie
        df['geometry'] = df['geometry'].apply(wkt.loads)
        gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:2154")
        

        df2 = conn.read(file_path2, input_format="csv")
        df2['geometry'] = df2['geometry'].apply(wkt.loads)
        gdf2 = gpd.GeoDataFrame(df2, geometry='geometry', crs="EPSG:2154")
        if gdf2['gridcode'].dtype != 'int64':
            # Utiliser pd.to_numeric avec errors='coerce' pour gérer les valeurs non-numériques
            # Ensuite, fillna(0) ou dropna() pour s'assurer qu'il n'y a plus de NaN (ici on suppose 0 par défaut si non valide)
            gdf2['gridcode'] = pd.to_numeric(gdf2['gridcode'], errors='coerce').fillna(0).astype(int)
        
        # CORRECTION CRITIQUE : Assurer que la colonne 'gridcode' est numérique
        if gdf['gridcode'].dtype != 'int64':
            # Utiliser pd.to_numeric avec errors='coerce' pour gérer les valeurs non-numériques
            # Ensuite, fillna(0) ou dropna() pour s'assurer qu'il n'y a plus de NaN (ici on suppose 0 par défaut si non valide)
            gdf['gridcode'] = pd.to_numeric(gdf['gridcode'], errors='coerce').fillna(0).astype(int)
        
        return (gdf,gdf2)

        
    except Exception as e:
        # st.error est préférable ici car il interrompt le flow pour cette section
        st.error(f"⚠️ Erreur lors du chargement des données pour le département {dept_code}: {e}")
        return None # Retourne None en cas d'échec


# Charger les données avec la fonction cachée
(gdf_projete , gdf_projete2) = load_and_prepare_data(departement)

if gdf_projete is None:
    st.stop() # Arrêter le script si les données n'ont pas pu être chargées

if gdf_projete2 is None:
    st.stop() # Arrêter le script si les données n'ont pas pu être chargées

# Définition du mapping (valeur : [couleur, label])
# Ajout de 3 pour 'Autres' au cas où des valeurs non-attendues seraient présentes après la correction
legend_mapping = {
    0: ['green', "Pas de risque (Nappe/Cave)"],
    1: ['yellow', "Aléa Débordement de Nappe"],
    2: ['blue', "Aléa Inondation de Cave"]
}


legend_mapping2 = {
    "Faible": ['green', "Risque faible"],
    "Moyen": ['yellow', "Risque moyen"],
    "Fort": ['red', "Risque fort"]
}
# ***************************************************************
# 4. Affichage et Conteneur Principal de la Carte
# ***************************************************************

st.subheader(f"Visualisation de l'Aléa Inondation pour le {departement}")

# Utiliser un conteneur pour organiser le graphique et la légende sous le titre
with st.container(border=True):
    
    # --- Configuration Matplotlib ---
    fig, ax = plt.subplots(figsize=(12, 12)) # Taille légèrement augmentée pour la clarté

    # Calcul des bornes
    minx, miny, maxx, maxy = gdf_projete.total_bounds
    x_buffer = (maxx - minx) * 0.02
    y_buffer = (maxy - miny) * 0.02
    
    ax.set_xlim(minx - x_buffer, maxx + x_buffer)
    ax.set_ylim(miny - y_buffer, maxy + y_buffer)
    ax.set_aspect('equal')
    ax.set_axis_off() # Pas besoin des axes X et Y pour une carte
    
    ax.set_title(f"Carte d'Aléa Basée sur le Gridcode - Département {departement}", fontsize=18)
    
    legend_handles = []
    legend_labels = [] 
    
    # Itération sur les classes numériques (0, 1, 2)
    with st.spinner("Génération de la carte..."): # Afficher un spinner pendant le tracé
        for code, (color, label) in legend_mapping.items():
            
            # 1. Filtrez le GeoDataFrame pour le code actuel
            # Assurez-vous d'utiliser une condition sécurisée après la conversion
            subset = gdf_projete[gdf_projete['gridcode'] == code]
            
            if not subset.empty:
                # 2. Tracez le sous-ensemble avec une couleur fixe
                subset.plot(
                    ax=ax,
                    color=color,
                    edgecolor='lightgray', # Changer la couleur de bordure pour une meilleure visibilité
                    linewidth=0.05,
                    alpha=0.8 # Ajout de transparence
                )
                
                # 3. Créez un objet Patch pour la légende
                legend_handles.append(Patch(facecolor=color, edgecolor='black', label=label))
                legend_labels.append(label)

    # Créer la légende discrète
    if legend_handles: # S'assurer qu'il y a des éléments à légender
        ax.legend(
            handles=legend_handles, 
            labels=legend_labels, 
            title="Grille de Code d'Aléa",
            loc='lower right', # Meilleure position pour la carte
            fancybox=True, 
            framealpha=0.85, # Légère opacité
            borderpad=1,
            fontsize=10
        )
    
    # Afficher le graphique Matplotlib dans Streamlit
    st.pyplot(fig, use_container_width=True)


 
with st.container(border=True):
    
    # --- Configuration Matplotlib ---
    fig, ax = plt.subplots(figsize=(12, 12)) # Taille légèrement augmentée pour la clarté

    # Calcul des bornes
    minx2, miny2, maxx2, maxy2 = gdf_projete2.total_bounds
    x_buffer2 = (maxx2 - minx2) * 0.02
    y_buffer2 = (maxy2 - miny2) * 0.02
    
    ax.set_xlim(minx2 - x_buffer2, maxx2 + x_buffer2)
    ax.set_ylim(miny2 - y_buffer2, maxy2 + y_buffer2)
    ax.set_aspect('equal')
    ax.set_axis_off() # Pas besoin des axes X et Y pour une carte
    
    ax.set_title(f"Carte de risque sécheresse - Département {departement}", fontsize=18)
    
    legend_handles2 = []
    legend_labels2 = [] 
    
    # Itération sur les classes numériques (0, 1, 2)
    with st.spinner("Génération de la carte..."): # Afficher un spinner pendant le tracé
        for code, (color, label) in legend_mapping2.items():
            
            # 1. Filtrez le GeoDataFrame pour le code actuel
            # Assurez-vous d'utiliser une condition sécurisée après la conversion
            subset2 = gdf_projete2[gdf_projete2['ALEA'] == code]
            
            if not subset2.empty:
                # 2. Tracez le sous-ensemble avec une couleur fixe
                subset.plot(
                    ax=ax,
                    color=color,
                    edgecolor='lightgray', # Changer la couleur de bordure pour une meilleure visibilité
                    linewidth=0.05,
                    alpha=0.8 # Ajout de transparence
                )
                
                # 3. Créez un objet Patch pour la légende
                legend_handles2.append(Patch(facecolor=color, edgecolor='black', label=label))
                legend_labels2.append(label)

    # Créer la légende discrète
    if legend_handles2: # S'assurer qu'il y a des éléments à légender
        ax.legend(
            handles=legend_handles2, 
            labels=legend_labels2, 
            title="Grille des risques",
            loc='lower right', # Meilleure position pour la carte
            fancybox=True, 
            framealpha=0.85, # Légère opacité
            borderpad=1,
            fontsize=10
        )
    
    # Afficher le graphique Matplotlib dans Streamlit
    st.pyplot(fig, use_container_width=True)
    
#    st.caption("Source des données : ")

# ***************************************************************
# 6. Fin et Bouton d'Action
# ***************************************************************
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Actualiser la Carte"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.success("Prêt à visualiser !")


