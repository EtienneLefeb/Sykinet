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

st.set_page_config(
    page_title="Carte d'Aléa d'Inondation et Sécheresse",
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.title("🗺️ Cartes d'Aléa du Département")
st.markdown("Visualisation des zones potentiellement sujettes aux débordements de nappe, inondations de cave, et risque sécheresse.")

# ***************************************************************
# 2. Sélecteur de Département dans la Barre Latérale (st.sidebar)
# ***************************************************************

with st.sidebar:
    st.header("Paramètres de la Carte")
    
    # Création de la liste des départements
    dep = [f"{i:02d}" for i in range(1, 96) if i != 20]
    dep.insert(19, "2A") 
    dep.insert(20, "2B") 
    
    @st.cache_data
    def get_department_list():
        return dep
        
    departement = st.selectbox(
        "Sélectionnez le Département",
        get_department_list(),
        index=30, # Index par défaut pour l'exemple
        help="Le code départemental (ex: 75 pour Paris)."
    )
    
    st.info(f"Département sélectionné : **{departement}**")

# ***************************************************************
# 3. Fonctions de Chargement des Données SÉPARÉES 
# ***************************************************************

# --- Fonction de chargement des données d'INONDATION ---
# Utilisation de st.secrets ou st.connection pour la connexion sécurisée
@st.cache_data(ttl=600)
def load_inondation_data(dept_code):
    try:
        # Assurez-vous que cette connexion est configurée dans votre environnement Streamlit Cloud
        conn = st.connection("gcs", type=FilesConnection) 
        file_path = f"streamlit-sykinet/base sykinet/base_innondation{dept_code}.csv"
        
        df = conn.read(file_path, input_format="csv")
        df['geometry'] = df['geometry'].apply(wkt.loads)
        gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:2154")
        
        # S'assurer que la colonne 'gridcode' est numérique
        if gdf['gridcode'].dtype != 'int64':
            gdf['gridcode'] = pd.to_numeric(gdf['gridcode'], errors='coerce').fillna(0).astype(int)
        
        return gdf
        
    except Exception as e:
        st.error(f"⚠️ Erreur lors du chargement des données d'inondation pour le département {dept_code}. Veuillez vérifier la configuration de la connexion GCS ou l'existence du fichier : {e}")
        return None 

# --- Fonction de chargement des données de SÉCHERESSE ---
@st.cache_data(ttl=600)
def load_secheresse_data(dept_code):
    try:
        # Assurez-vous que cette connexion est configurée dans votre environnement Streamlit Cloud
        conn = st.connection("gcs", type=FilesConnection) 
        file_path = f"streamlit-sykinet/base sykinet/df_secheresse{dept_code}.csv"
        
        df = conn.read(file_path, input_format="csv")
        df['geometry'] = df['geometry'].apply(wkt.loads)
        gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:2154")
        
        # S'assurer que la colonne 'ALEA' est présente et de type string pour la légende
        if 'ALEA' not in gdf.columns:
            st.warning("La colonne 'ALEA' est manquante dans les données de sécheresse. Impossible de générer la carte.")
            return None
        
        return gdf
        
    except Exception as e:
        st.error(f"⚠️ Erreur lors du chargement des données de sécheresse pour le département {dept_code}. Veuillez vérifier la configuration de la connexion GCS ou l'existence du fichier : {e}")
        return None

# ***************************************************************
# 4. Appel des Fonctions de Chargement
# ***************************************************************

# Conteneur pour afficher un message de chargement pendant l'appel
loading_placeholder = st.empty()
loading_placeholder.info(f"Chargement des données de cartographie pour le département {departement}...")

gdf_inondation = load_inondation_data(departement)
gdf_secheresse = load_secheresse_data(departement)

loading_placeholder.empty() # Effacer le message de chargement une fois terminé

# Arrêter l'exécution si l'une des cartes manque
if gdf_inondation is None or gdf_secheresse is None:
    st.error("Impossible de poursuivre : au moins une source de données est manquante ou a échoué au chargement.")
    st.stop()

# Définitions de légendes
legend_mapping_inondation = {
    0: ['#4CAF50', "Pas de risque (Nappe/Cave)"], # Vert
    1: ['#FFC107', "Aléa Débordement de Nappe"], # Jaune/Orange
    2: ['#2196F3', "Aléa Inondation de Cave"] # Bleu
}

# --- LÉGENDE DE SÉCHERESSE MODIFIÉE POUR RESPECTER L'ÉCHELLE D'IMPORTANCE ---
legend_mapping_secheresse = {
    "Nul": ["#E8F5E9",'Pas de risque (Nul)'], # Vert très clair, proche du blanc
    "Faible": ['#4CAF50', "Risque faible"],    # Vert
    "Moyen": ['#FFC107', "Risque moyen"],    # Jaune/Orange
    "Fort": ['#F44336', "Risque fort"]      # Rouge
}

# ***************************************************************
# 5. Affichage de la Carte d'Inondation
# ***************************************************************

st.header("🌊 Carte d'Aléa Inondation")

with st.container(border=True):
    
    # --- Configuration Matplotlib ---
    fig_inondation, ax_inondation = plt.subplots(figsize=(12, 12)) 

    # Calcul des bornes
    minx, miny, maxx, maxy = gdf_inondation.total_bounds
    x_buffer = (maxx - minx) * 0.02
    y_buffer = (maxy - miny) * 0.02
    
    ax_inondation.set_xlim(minx - x_buffer, maxx + x_buffer)
    ax_inondation.set_ylim(miny - y_buffer, maxy + y_buffer)
    ax_inondation.set_aspect('equal')
    ax_inondation.set_axis_off() 
    ax_inondation.set_title(f"Carte d'Aléa Basée sur le Gridcode - Département {departement}", fontsize=18)
    
    legend_handles = []
    
    with st.spinner("Génération de la carte d'inondation..."):
        # Dessiner le fond (par exemple, les zones sans risque ou l'ensemble du département)
        gdf_inondation.plot(
            ax=ax_inondation,
            color='lightgrey', # Couleur de fond par défaut
            edgecolor='white',
            linewidth=0.01,
            alpha=0.5
        )

        for code, (color, label) in legend_mapping_inondation.items():
            subset = gdf_inondation[gdf_inondation['gridcode'] == code]
            
            if not subset.empty:
                subset.plot(
                    ax=ax_inondation,
                    color=color,
                    edgecolor='lightgray',
                    linewidth=0.05,
                    alpha=0.9
                )
                legend_handles.append(Patch(facecolor=color, edgecolor='black', label=label))

    # Créer la légende discrète
    if legend_handles: 
        ax_inondation.legend(
            handles=legend_handles, 
            title="Grille de Code d'Aléa",
            loc='lower right', 
            fancybox=True, 
            framealpha=0.85, 
            borderpad=1,
            fontsize=10
        )
    
    st.pyplot(fig_inondation, use_container_width=True)


# ***************************************************************
# 6. Affichage de la Carte de Sécheresse
# ***************************************************************

st.header("☀️ Carte de Risque Sécheresse")

with st.container(border=True):
    
    # --- Configuration Matplotlib ---
    fig_secheresse, ax_secheresse = plt.subplots(figsize=(12, 12)) 

    # Calcul des bornes (utilisez les bornes de gdf_secheresse)
    minx2, miny2, maxx2, maxy2 = gdf_secheresse.total_bounds
    x_buffer2 = (maxx2 - minx2) * 0.02
    y_buffer2 = (maxy2 - miny2) * 0.02
    
    ax_secheresse.set_xlim(minx2 - x_buffer2, maxx2 + x_buffer2)
    ax_secheresse.set_ylim(miny2 - y_buffer2, maxy2 + y_buffer2)
    ax_secheresse.set_aspect('equal')
    ax_secheresse.set_axis_off() 
    ax_secheresse.set_title(f"Carte de risque sécheresse - Département {departement}", fontsize=18)
    
    legend_handles2 = []
    
    # Dessiner le fond de la carte de sécheresse
    gdf_secheresse.plot(
        ax=ax_secheresse,
        color='lightgrey', 
        edgecolor='white',
        linewidth=0.01,
        alpha=0.5
    )

    # Itération sur les classes de texte ("Nul", "Faible", "Moyen", "Fort")
    with st.spinner("Génération de la carte sécheresse..."):
        for code, (color, label) in legend_mapping_secheresse.items():
            
            # Utilisation de la colonne 'ALEA' comme spécifié dans votre code
            subset2 = gdf_secheresse[gdf_secheresse['ALEA'] == code]
            
            if not subset2.empty:
                subset2.plot(
                    ax=ax_secheresse,
                    color=color,
                    edgecolor='lightgray',
                    linewidth=0.05,
                    alpha=0.9
                )
                legend_handles2.append(Patch(facecolor=color, edgecolor='black', label=label))

    # Créer la légende discrète
    if legend_handles2: 
        ax_secheresse.legend(
            handles=legend_handles2, 
            title="Grille des risques",
            loc='lower right', 
            fancybox=True, 
            framealpha=0.85, 
            borderpad=1,
            fontsize=10
        )
    
    st.pyplot(fig_secheresse, use_container_width=True)

# ***************************************************************
# 7. Fin et Bouton d'Action
# ***************************************************************
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Actualiser les Cartes (Vider le cache)"):
    # Vider le cache de toutes les fonctions @st.cache_data
    st.cache_data.clear()
    st.rerun()

st.sidebar.success("Prêt à visualiser !")