import streamlit as st
import geopandas as gpd
import pandas as pd
from shapely import wkt
from st_files_connection import FilesConnection  # Import nécessaire pour la connexion GCS
import matplotlib.pyplot as plt
import numpy as np
from io import StringIO

# IMPORTANT:
# Cette version utilise la connexion GCS (st_files_connection) pour charger les données réelles.
# Assurez-vous que cette librairie est installée et que la connexion "gcs" est configurée.

# --- Fonction de chargement des données réelles (activée) ---

@st.cache_data
def load_real_data(file_path, column_calc_type):
    """
    Charge les données depuis Google Cloud Storage (GCS) via FilesConnection, 
    convertit la géométrie WKT et calcule la colonne 'NIVEAU'.
    """
    conn = st.connection("gcs", type=FilesConnection) 
    df = conn.read(file_path, input_format="csv")
    
    # Conversion de la géométrie WKT
    df['geometry'] = df['geometry'].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:2154")
    
    if column_calc_type == "secheresse":
        # Votre formule originale pour la sécheresse : (Moyen + Fort) / Total
        total_pct = gdf["pct_nulle"] + gdf["pct_faible"] + gdf["pct_moyen"] + gdf["pct_fort"]
        # Éviter la division par zéro
        gdf["NIVEAU"] = np.where(total_pct > 0, (gdf["pct_moyen"] + gdf["pct_fort"]) / total_pct, 0)
        
    elif column_calc_type == "innondation":
        # Votre formule originale pour l'inondation : (Caves + Nappes) / Total
        total_pct = gdf["pct_innond_caves"] + gdf["pct_debord_nappes"] + gdf["pct_sans_risque"]
        # Éviter la division par zéro
        gdf["NIVEAU"] = np.where(total_pct > 0, (gdf["pct_innond_caves"] + gdf["pct_debord_nappes"]) / total_pct, 0)

    return gdf

# --- Fonction de Création de Carte Modulaire ---

def create_risk_map(gdf_data, title, cmap_color='viridis'):
    """
    Crée et affiche une carte choroplèthe Matplotlib à partir d'un GeoDataFrame.
    """
    # 1. Créer la figure et l'axe Matplotlib
    # Utiliser un rapport hauteur/largeur pour l'Europe/France
    fig, ax = plt.subplots(1, 1, figsize=(10, 8)) 

    # 2. Tracer le GeoDataFrame
    gdf_data.plot(
        column='NIVEAU', 
        ax=ax, 
        legend=True, 
        cmap=cmap_color, 
        edgecolor='gray', # Bordure plus douce
        linewidth=0.3,
        legend_kwds={
            'label': "Proportion de Zone à Risque (0.0 à 1.0)",
            'orientation': "horizontal",
            'shrink': 0.7, # Légende plus compacte
            'pad': 0.05,
            'aspect': 30 # Pour une barre plus fine
        },
        missing_kwds={
            "color": "lightgrey",
            "edgecolor": "black",
            "hatch": "///",
            "label": "Donnée Manquante",
        }
    )

    # 3. Personnaliser la carte
    ax.set_title(title, fontsize=16, pad=20)
    ax.set_axis_off() 
    
    # 4. Afficher la carte
    st.pyplot(fig)

# ***************************************************************
# 1. Configuration de la Page et Titre Principal
# ***************************************************************

st.set_page_config(
    page_title="Résumé des données climatiques",
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.title("🗺️ Analyse Géospatiale des Risques Climatiques")
st.markdown("""
Cette page présente les premières représentations cartographiques des zones les plus exposées 
à l'**aléa sécheresse** (Retrait-Gonflement des Argiles ou RGA) et à l'**aléa inondation**. 
Le niveau de risque est calculé en fonction de la proportion de la zone considérée comme étant à risque modéré ou fort.
""")

st.divider()

# --- Chargement des données (Utiliser les fonctions de simulation/réelles) ---

# Configuration pour les données réelles (Chemins d'accès GCS)
RGA_FILE_PATH = "streamlit-sykinet/base sykinet/df_secheresse_complet.csv"
INNONDATION_FILE_PATH = "streamlit-sykinet/base sykinet/df_innond_complet.csv"

# Appel des fonctions de chargement réel
gdf_rga = load_real_data(RGA_FILE_PATH, "secheresse")
gdf_innondation = load_real_data(INNONDATION_FILE_PATH, "innondation")

# Suppression de la note d'information sur les données simulées (qui ne sont plus utilisées)
# st.info("⚠️ **Note:** Les cartes affichées utilisent des données et des géométries simulées pour des raisons de démonstration. Les valeurs de risque sont arbitraires.")


# ***************************************************************
# 2. Organisation du Contenu avec des Onglets
# ***************************************************************

tab1, tab2 = st.tabs(["🔥 Risque Sécheresse (RGA)", "💧 Risque Inondation (Nappes/Caves)"])

with tab1:
    st.header("Analyse du Risque de Sécheresse (RGA)")
    st.markdown("""
    Le risque de Retrait-Gonflement des Argiles (RGA) est un aléa majeur en France, 
    causant des dommages importants aux habitations individuelles.
    La carte ci-dessous visualise la **proportion de la zone** exposée à un risque moyen ou fort de RGA.
    """)
    
    # Utilisation de la fonction modulaire
    create_risk_map(
        gdf_rga, 
        "Carte des départements les plus touchés par le risque RGA",
        cmap_color='YlOrRd' # Utiliser des couleurs chaudes pour la sécheresse
    )

    # st.subheader("Détails du Calcul")
    # st.code(
    #     """
    #     NIVEAU = (pct_moyen + pct_fort) / 
    #              (pct_nulle + pct_faible + pct_moyen + pct_fort)
    #     """
    # )

with tab2:
    st.header("Analyse du Risque d'Inondation")
    st.markdown("""
    Ce risque combine la submersion des caves et le débordement des nappes phréatiques.
    La carte montre la **proportion de la zone** où ces deux types d'aléas sont présents.
    """)
    
    # Utilisation de la fonction modulaire
    create_risk_map(
        gdf_innondation, 
        "Carte des départements les plus touchés par le risque inondation",
        cmap_color='Blues' # Utiliser des couleurs froides pour l'eau/inondation
    )

    # st.subheader("Détails du Calcul")
    # st.code(
    #     """
    #     NIVEAU = (pct_innond_caves + pct_debord_nappes) / 
    #              (pct_innond_caves + pct_debord_nappes + pct_sans_risque)
    #     """
    # )

st.sidebar.markdown("## Paramètres de Visualisation")
st.sidebar.markdown("Pour l'instant, les cartes affichent la vue globale. Des filtres par période ou intensité pourront être ajoutés ici.")