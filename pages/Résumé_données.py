import streamlit as st
import geopandas as gpd
import pandas as pd
from shapely import wkt
from st_files_connection import FilesConnection  # Import nécessaire pour la connexion GCS
import matplotlib.pyplot as plt
import numpy as np
from io import StringIO
import seaborn as sns # Ajouté pour l'harmonisation de l'analyse des Maisons

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
    fig, ax = plt.subplots(1, 1, figsize=(8, 6)) 

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

# --- Fonction de Création d'Histogramme Modulaire ---

def create_risk_histogram(gdf_data, title, color='skyblue'):
    """
    Crée et affiche un histogramme de la distribution de la variable 'NIVEAU'.
    """
    # Créer la figure et l'axe Matplotlib
    fig, ax = plt.subplots(1, 1, figsize=(8, 5)) 

    # Tracer l'histogramme
    ax.hist(gdf_data['NIVEAU'].dropna(), bins=15, range=(0, 1), edgecolor='black', color=color, alpha=0.7)

    # Personnaliser le graphique
    ax.set_title(title, fontsize=16)
    ax.set_xlabel("Niveau de Risque (Proportion de la zone affectée, de 0.0 à 1.0)")
    ax.set_ylabel("Nombre de Zones (Départements)")
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    
    # Limiter l'axe des x de 0 à 1 (puisque NIVEAU est une proportion)
    ax.set_xlim(0, 1)

    # Afficher le graphique dans Streamlit
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

# --- Chargement des données ---

# Configuration pour les données réelles (Chemins d'accès GCS)
RGA_FILE_PATH = "streamlit-sykinet/base sykinet/df_secheresse_complet.csv"
INNONDATION_FILE_PATH = "streamlit-sykinet/base sykinet/df_innond_complet.csv"

# Appel des fonctions de chargement réel
gdf_rga = load_real_data(RGA_FILE_PATH, "secheresse")
gdf_innondation = load_real_data(INNONDATION_FILE_PATH, "innondation")


# ***************************************************************
# 2. Organisation du Contenu avec des Onglets et Analyse Condensée
# ***************************************************************

tab1, tab2 = st.tabs(["🔥 Risque Sécheresse (RGA)", "💧 Risque Inondation (Nappes/Caves)"])

with tab1:
    st.header("Analyse du Risque de Sécheresse (RGA)")
    st.markdown("""
    Le risque de Retrait-Gonflement des Argiles (RGA) est un aléa majeur en France, 
    causant des dommages importants aux habitations individuelles.
    """)
    
    col_map, col_hist = st.columns(2)

    with col_map:
        st.subheader("Distribution Géographique du Risque")
        create_risk_map(
            gdf_rga, 
            "Carte des départements les plus touchés par le risque RGA",
            cmap_color='YlOrRd'
        )

    with col_hist:
        st.subheader("Répartition du Niveau de Risque (Histogramme)")
        create_risk_histogram(
            gdf_rga, 
            "Distribution des Niveaux de Risque RGA par Département",
            color='orange'
        )
        
    st.markdown("#### 🔍 Synthèse des Observations (RGA)")
    st.info("""
    **Cohérence Géologique :** La carte choroplèthe montre une forte adéquation avec les réalités géologiques, mettant en lumière l'hétérogénéité territoriale du risque RGA.
    
    * **Zones à Risque Élevé :** Principalement concentrées dans le Sud-Ouest (Gers, Lot-et-Garonne, Tarn-et-Garonne) et le Centre (Indre-et-Loire, Cher).
    * **Zones à Risque Faible :** Majoritairement les zones côtières et montagneuses (Bretagne, Alpes, Massif Central).

    **Analyse de l'Histogramme :**
    * La distribution n'est pas uniforme, confirmant le contraste entre régions.
    * Une **majorité des départements** se situe dans des niveaux moyens de risque (proportion de zones à risque entre **0.2 et 0.7**).

    **Conclusion Actuarielle :** Ces visualisations sont essentielles pour l'évaluation du risque et la tarification des assurances, car elles permettent de cibler précisément les zones d'actions de prévention et de rénovation.
    """)


with tab2:
    st.header("Analyse du Risque d'Inondation")
    st.markdown("""
    Ce risque combine la submersion des caves et le débordement des nappes phréatiques.
    """)
    
    col_map, col_hist = st.columns(2)
    
    with col_map:
        st.subheader("Distribution Géographique du Risque")
        create_risk_map(
            gdf_innondation, 
            "Carte des départements les plus touchés par le risque inondation",
            cmap_color='Blues'
        )

    with col_hist:
        st.subheader("Répartition du Niveau de Risque (Histogramme)")
        create_risk_histogram(
            gdf_innondation, 
            "Distribution des Niveaux de Risque Inondation par Département",
            color='blue'
        )
        
    st.markdown("#### 🔍 Synthèse des Observations (Inondation)")
    st.info("""
    **Hétérogénéité Spatiale :** La carte met en évidence une forte hétérogénéité spatiale du risque d’inondation en France.
    
    * **Zones Fortement Exposées :** La région **Centre–Val de Loire**, certains départements des Hauts-de-France et le Sud-Ouest. Le département des **Bouches-du-Rhône** ressort comme particulièrement vulnérable (confirmant les épisodes récents autour de Marseille).
    * **Zones Faiblement Exposées :** Des régions comme **Auvergne–Rhône-Alpes** et les zones montagneuses, où la géomorphologie est moins favorable aux débordements.

    **Analyse de l'Histogramme :**
    * La majorité des départements se concentre autour de niveaux intermédiaires, entre **20 % et 40 %** de zones à risque.
    * Un nombre important de départements présente une exposition inférieure à 20 % (zones claires de la carte).
    * Quelques départements dépassent **50 %**, constituant des zones extrêmes essentielles pour la gestion du risque maximal.

    **Conclusion Actuarielle :** Ces résultats permettent d'identifier précisément les localisations les plus vulnérables pour l'ajustement des primes d'assurance, la tarification et le renforcement des modèles de risque.
    """)