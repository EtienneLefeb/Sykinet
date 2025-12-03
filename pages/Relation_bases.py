import streamlit as st
import geopandas as gpd
import pandas as pd
from shapely import wkt
# Import nécessaire pour la connexion GCS (Gardé)
from st_files_connection import FilesConnection 
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
# On ajoute Plotly pour des graphiques interactifs (Recommandé)
import plotly.express as px

# --- 1. CONFIGURATION DE PAGE ---
st.set_page_config(
    page_title="Risques Climatiques et Valeurs Foncières",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. TITRE ET INTRODUCTION ---
st.title("Mise en relation des risques climatiques et des valeurs foncières 🏠📊")

st.markdown("""
Cette application analyse l'impact des **risques d'inondation** et de **sécheresse** sur la **valeur foncière** des appartements dans les régions Nouvelle Aquitaine, Occitanie et Centre-Val de Loire.
""")

# Utilisation d'un expander pour cacher le texte d'introduction si nécessaire
with st.expander("Détails de la méthodologie"):
    st.markdown("""
    La base de données des valeurs foncières a été réduite aux ventes d'appartements et limitée aux régions de Nouvelle Aquitaine, d'Occitanie et de Centre-Val de Loire, où les risques sécheresse et inondations sont avérés.
    """)

path = "streamlit-sykinet/base sykinet/"
conn = st.connection("gcs", type=FilesConnection)

# --- 3. ANALYSE DU RISQUE D'INONDATION ---
st.header("Analyse du Risque d'Inondation 🌊")
st.markdown("---")

# Chargement des données d'inondation
df_resultat_innond_final = conn.read(path + "base_innond_final.csv", input_format="csv")

# Création de 2 colonnes pour afficher côte à côte le décompte et le scatter
col1_inond, col2_inond = st.columns(2)

with col1_inond:
    st.subheader("Répartition des types de Risques d'Inondation")
    counts = df_resultat_innond_final['Risque_innond'].value_counts()
    
    # Création d'un graphique à barres plus propre avec Streamlit/Matplotlib
    fig = plt.figure(figsize=(15,6))
    counts.plot(kind='bar', color=['#2196F3', '#4CAF50', '#FFC107']) # Couleurs claires
    plt.xlabel("Type de Risque d'inondation")
    plt.ylabel("Nombre de transactions")
    plt.xticks(rotation=0) # Améliore la lisibilité des étiquettes
    plt.tight_layout()
    st.pyplot(fig)

with col2_inond:
    st.subheader("Valeur Foncière vs. Surface (Filtrée)")
    # Reformatage des données pour le scatter plot
    df_plot_inond = df_resultat_innond_final.copy()
    
    # Filtrer pour avoir une meilleure visualisation (comme dans le code original)
    df_plot_inond = df_plot_inond[(df_plot_inond["surface_reelle_bati"] < 400) & (df_plot_inond["valeur_fonciere"] < 1e6)]
    
    # UTILISATION DE PLOTLY pour un scatter interactif et plus beau
    fig2_plotly = px.scatter(
        df_plot_inond,
        x="surface_reelle_bati",
        y="valeur_fonciere",
        color="Risque_innond",
        hover_name="Risque_innond",
        title="Valeur Foncière par Surface selon le Risque",
        color_discrete_map={
            "Pas de débordement de nappe ni d'inondation de cave": '#4CAF50',
            "Zones potentiellement sujettes aux inondations de cave": '#2196F3',
            "Zones potentiellement sujettes aux débordements de nappe": '#FFC107'
        }
    )
    fig2_plotly.update_layout(height=400)
    st.plotly_chart(fig2_plotly, use_container_width=True)

# Box Plot pour le risque inondation
st.subheader("Impact du Risque sur le Prix/m² (Inondation)")
df_resultat_innond_final["valeur_fonciere_par_surface"] = df_resultat_innond_final['valeur_fonciere']/df_resultat_innond_final['surface_reelle_bati']
df_resultat_innond_final = df_resultat_innond_final[~df_resultat_innond_final["Risque_innond"].isna()]

# Nettoyage des outliers extrêmes pour le graphique (ylim à 1e4)
df_innond_filtered = df_resultat_innond_final[df_resultat_innond_final["valeur_fonciere_par_surface"] < 1e4]

fig3 = plt.figure(figsize=(25, 10))
sns.boxplot(
    x='Risque_innond', 
    y='valeur_fonciere_par_surface', 
    data=df_innond_filtered,
    palette=['#4CAF50', '#2196F3', '#FFC107'] # Palette cohérente
)
plt.title('Distribution du Prix/m² en fonction du Type de Risque d\'Inondation')
plt.xlabel("Type de Risque d'Inondation")
plt.ylabel('Prix au m² (Valeur Foncière / Surface Bâtie)')
plt.xticks(rotation=15, ha='right') # Rotation pour lisibilité
plt.tight_layout()
st.pyplot(fig3)


# ... (Partie Inondation)

# --- 4. ANALYSE DU RISQUE SÉCHERESSE ---
st.header("Analyse du Risque Sécheresse 🏜️")
st.markdown("---")

# Chargement des données de sécheresse (déjà présent)
df_resultat = conn.read(path + "base_sech_final.csv", input_format="csv") 
df_resultat["valeur_fonciere_par_surface"] = df_resultat['valeur_fonciere']/df_resultat['surface_reelle_bati']


# NOUVEAU : Deux colonnes pour la distribution et le scatter
col1_sech_dist, col2_sech_scatter = st.columns(2)

# --- NOUVEAU GRAPHIQUE : RÉPARTITION DU RISQUE SÉCHERESSE ---
with col1_sech_dist:
    st.subheader("Répartition des Niveaux de Risque Sécheresse")
    
    # 1. Compter les occurrences
    secheresse_counts = df_resultat['zone_niveau'].value_counts().sort_index()
    
    # 2. Créer la figure Matplotlib
    fig_sech_dist = plt.figure(figsize=(6,4))
    secheresse_counts.plot(
        kind='bar', 
        color=['#4CAF50', '#FFC107', '#F44336', '#B71C1C'] # Dégradé de risque
    )
    plt.xlabel("Niveau de Risque Sécheresse")
    plt.ylabel("Nombre de transactions")
    plt.title("Répartition des Niveaux de Risque (0.0 à 3.0)")
    plt.xticks(rotation=0)
    plt.tight_layout()
    st.pyplot(fig_sech_dist)


with col2_sech_scatter:
    st.subheader("Valeur Foncière vs. Surface selon le Niveau de Sécheresse")
    
    # Filtrer les données pour le graphique scatter (comme dans l'original)
    df_plot_sech = df_resultat[(df_resultat["surface_reelle_bati"] < 400) & (df_resultat["valeur_fonciere"] < 1e6)].copy()
    
    # S'assurer que 'zone_niveau' est traité comme catégorie pour la couleur
    df_plot_sech['zone_niveau_str'] = df_plot_sech['zone_niveau'].astype(str)
    
    # UTILISATION DE PLOTLY pour un scatter interactif
    fig4_plotly = px.scatter(
        df_plot_sech,
        x="surface_reelle_bati",
        y="valeur_fonciere",
        color="zone_niveau_str",
        hover_name="zone_niveau_str",
        title="Impact du Niveau de Sécheresse",
        labels={'zone_niveau_str': 'Niveau Sécheresse'},
        color_discrete_sequence=['#E8F5E9', '#4CAF50', '#FFC107', '#F44336']
    )
    fig4_plotly.update_layout(height=450)
    st.plotly_chart(fig4_plotly, use_container_width=True)


# Le Box Plot reste en pleine largeur en dessous des deux graphiques
st.subheader("Impact du Risque sur le Prix/m² (Sécheresse)")

# Nettoyage des outliers extrêmes pour le graphique (ylim à 1e4)
df_sech_filtered = df_resultat[df_resultat["valeur_fonciere_par_surface"] < 1e4]

fig5 = plt.figure(figsize=(10, 6))
sns.boxplot(
    x='zone_niveau', 
    y='valeur_fonciere_par_surface', 
    data=df_sech_filtered,
    order=[0.0, 1.0, 2.0, 3.0], 
    palette=['#4CAF50', '#FFC107', '#F44336', '#B71C1C']
)
plt.title('Distribution du Prix/m² par Niveau de Risque Sécheresse')
plt.xlabel('Niveau de Risque Sécheresse (0.0: Très Faible, 3.0: Très Fort)')
plt.ylabel('Prix au m² (Valeur Foncière / Surface Bâtie)')
plt.tight_layout()
st.pyplot(fig5)