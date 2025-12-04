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
Cette application analyse l'impact des **risques d'inondation** et de **sécheresse** sur la **valeur foncière** des biens dans trois grandes régions.
""")

# Utilisation d'un expander pour cacher le texte d'introduction si nécessaire
with st.expander("Détails de la méthodologie"):
    st.markdown("""
    **Analyse des Appartements (Bâti Uniquement) :**
    La base de données des appartements a été réduite aux ventes dans les régions ciblées. Comme le prix réfère principalement à l'appartement lui-même, nous avons utilisé comme unité de mesure le **prix par mètre carré bâti**.

    **Analyse des Maisons (Bâti + Terrain) :**
    La base des maisons est plus complexe car le prix total inclut le bâtiment et la surface du terrain. Pour pouvoir faire des comparaisons significatives, nous avons sélectionné des maisons aux caractéristiques similaires (surface du terrain entre 300 et 400 $m^2$ et surface du bâtiment entre 80 et 105 $m^2$). L'unité de mesure choisie est le **prix par mètre carré de surface de terrain**.
    """)

path = "streamlit-sykinet/base sykinet/"
conn = st.connection("gcs", type=FilesConnection)

# ==============================================================================
# SECTION 1 : APPARTEMENTS
# ==============================================================================
st.header("1. Analyse pour les Appartements 🏢")
st.markdown("---")

# Chargement des données d'inondation
df_resultat_innond_final = conn.read(path + "base_innond_final.csv", input_format="csv")

# --- Risque Inondation (Appartements) ---
st.subheader("Risque d'Inondation : Distribution et Impact sur le Prix/m² Bâti")
col1_inond, col2_inond = st.columns(2)

with col1_inond:
    st.markdown("##### Répartition des Types de Risques d'Inondation")
    counts = df_resultat_innond_final['Risque_innond'].value_counts()
    
    fig = plt.figure(figsize=(12,6))
    counts.plot(kind='bar', color=['#2196F3', '#4CAF50', '#FFC107'])
    plt.xlabel("Type de Risque d'inondation")
    plt.ylabel("Nombre de transactions")
    # Rotation des labels pour la lisibilité
    plt.xticks(rotation=45, ha='right') 
    plt.tight_layout()
    st.pyplot(fig)

with col2_inond:
    st.markdown("##### Valeur Foncière vs. Surface (Filtrée)")
    df_plot_inond = df_resultat_innond_final.copy()
    df_plot_inond = df_plot_inond[(df_plot_inond["surface_reelle_bati"] < 400) & (df_plot_inond["valeur_fonciere"] < 1e6)]
    
    fig2_plotly = px.scatter(
        df_plot_inond,
        x="surface_reelle_bati",
        y="valeur_fonciere",
        color="Risque_innond",
        hover_name="Risque_innond",
        title="Valeur Foncière par Surface selon le Risque",
        color_discrete_map={
            "Pas de risques": '#4CAF50',
            "Inondations de cave": '#2196F3',
            "Débordements de nappe": '#FFC107'
        }
    )
    fig2_plotly.update_layout(height=400)
    st.plotly_chart(fig2_plotly, use_container_width=True)


st.markdown("##### Box Plot : Prix au $m^2$ Bâti en fonction du Risque d'Inondation")
df_resultat_innond_final["valeur_fonciere_par_surface"] = df_resultat_innond_final['valeur_fonciere']/df_resultat_innond_final['surface_reelle_bati']
df_innond_filtered = df_resultat_innond_final[~df_resultat_innond_final["Risque_innond"].isna()]
df_innond_filtered = df_innond_filtered[df_innond_filtered["valeur_fonciere_par_surface"] < 1e4] # Nettoyage des outliers

fig3 = plt.figure(figsize=(10, 6))
sns.boxplot(
    x='Risque_innond', 
    y='valeur_fonciere_par_surface', 
    data=df_innond_filtered,
    palette=['#4CAF50', '#2196F3', '#FFC107']
)
plt.title('Distribution du Prix/m² Bâti en fonction du Type de Risque d\'Inondation (Appartements)')
plt.xlabel("Type de Risque d'Inondation")
plt.ylabel('Prix au $m^2$ (Valeur Foncière / Surface Bâtie)')
plt.xticks(rotation=45, ha='right') 
plt.tight_layout()
st.pyplot(fig3)


# --- Risque Sécheresse (Appartements) ---
st.subheader("Risque Sécheresse : Distribution et Impact sur le Prix/m² Bâti")
df_resultat = conn.read(path + "base_sech_final.csv", input_format="csv") 
df_resultat["valeur_fonciere_par_surface"] = df_resultat['valeur_fonciere']/df_resultat['surface_reelle_bati']

col1_sech_dist, col2_sech_scatter = st.columns(2)

with col1_sech_dist:
    st.markdown("##### Répartition des Niveaux de Risque Sécheresse")
    
    secheresse_counts = df_resultat['zone_niveau'].value_counts().sort_index()
    
    fig_sech_dist = plt.figure(figsize=(6,4))
    secheresse_counts.plot(
        kind='bar', 
        color=['#4CAF50', '#FFC107', '#F44336', '#B71C1C']
    )
    plt.xlabel("Niveau de Risque Sécheresse")
    plt.ylabel("Nombre de transactions")
    plt.title("Répartition des Niveaux de Risque (0.0 à 3.0)")
    plt.xticks(rotation=0)
    plt.tight_layout()
    st.pyplot(fig_sech_dist)


with col2_sech_scatter:
    st.markdown("##### Valeur Foncière vs. Surface selon le Niveau de Sécheresse")
    
    df_plot_sech = df_resultat[(df_resultat["surface_reelle_bati"] < 400) & (df_resultat["valeur_fonciere"] < 1e6)].copy()
    df_plot_sech['zone_niveau_str'] = df_plot_sech['zone_niveau'].astype(str)
    df_plot_sech = df_plot_sech.dropna().sort_values(by = "zone_niveau_str")
    
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


st.markdown("##### Box Plot : Prix au $m^2$ Bâti en fonction du Risque Sécheresse")
df_sech_filtered = df_resultat[df_resultat["valeur_fonciere_par_surface"] < 1e4]

fig5 = plt.figure(figsize=(10, 6))
sns.boxplot(
    x='zone_niveau', 
    y='valeur_fonciere_par_surface', 
    data=df_sech_filtered,
    order=[0.0, 1.0, 2.0, 3.0], 
    palette=['#4CAF50', '#FFC107', '#F44336', '#B71C1C']
)
plt.title('Distribution du Prix/m² Bâti par Niveau de Risque Sécheresse (Appartements)')
plt.xlabel('Niveau de Risque Sécheresse (0.0: Très Faible, 3.0: Très Fort)')
plt.ylabel('Prix au $m^2$ (Valeur Foncière / Surface Bâtie)')
plt.xticks(rotation=0)
plt.tight_layout()
st.pyplot(fig5)


# ==============================================================================
# SECTION 2 : MAISONS
# ==============================================================================
st.header("2. Analyse pour les Maisons (Bâti + Terrain) 🏡")
st.markdown("---")

# --- Risque Inondation (Maisons) ---
st.subheader("Risque d'Inondation : Distribution et Impact sur le Prix/m² Terrain")

df_resultat_innond_maison_final = conn.read(path + "base_innond_final_maison.csv", input_format="csv")
df_resultat_innond_maison_final["valeur_fonciere_par_surface"] = df_resultat_innond_maison_final['valeur_fonciere']/df_resultat_innond_maison_final['surface_terrain']


col1_maison_inond_dist, col2_maison_inond_box = st.columns(2)

with col1_maison_inond_dist:
    st.markdown("##### Répartition des Types de Risques d'Inondation (Maisons)")
    counts_maison_inond = df_resultat_innond_maison_final['Risque_innond'].value_counts()

    fig7 = plt.figure(figsize=(10,6))
    counts_maison_inond.plot(kind='bar', color=['#2196F3', '#4CAF50', '#FFC107'])
    plt.xlabel("Type de Risque d'inondation")
    plt.ylabel("Nombre de transactions")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig7)

with col2_maison_inond_box:
    st.markdown("##### Box Plot : Prix au $m^2$ Terrain en fonction du Risque d'Inondation")
    df_maison_inond_filtered = df_resultat_innond_maison_final[df_resultat_innond_maison_final["valeur_fonciere_par_surface"] < 1.4e3]

    fig8 = plt.figure(figsize=(10, 6))
    sns.boxplot(
        x='Risque_innond', 
        y='valeur_fonciere_par_surface', 
        data=df_maison_inond_filtered,
        palette=['#4CAF50', '#2196F3', '#FFC107']
    )
    plt.title('Distribution du Prix/m² Terrain par Risque d\'Inondation (Maisons)')
    plt.xlabel("Type de Risque d'Inondation")
    plt.ylabel('Prix au $m^2$ Terrain (Valeur Foncière / Surface Terrain)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig8)


# --- Risque Sécheresse (Maisons) ---
st.subheader("Risque Sécheresse : Distribution et Impact sur le Prix/m² Terrain")

df_resultat_maison = conn.read(path + "base_sech_final_maison.csv", input_format="csv") 
df_resultat_maison["valeur_fonciere_par_surf"] = df_resultat_maison["valeur_fonciere"] / df_resultat_maison["surface_terrain"]

col1_maison_sech_dist, col2_maison_sech_box = st.columns(2)

with col1_maison_sech_dist:
    st.markdown("##### Répartition des Niveaux de Risque Sécheresse (Maisons)")
    
    secheresse_counts_maison = df_resultat_maison['zone_niveau'].value_counts().sort_index()
    
    fig_sech_maison_dist = plt.figure(figsize=(6,4))
    secheresse_counts_maison.plot(
        kind='bar', 
        color=['#4CAF50', '#FFC107', '#F44336', '#B71C1C']
    )
    plt.xlabel("Niveau de Risque Sécheresse")
    plt.ylabel("Nombre de transactions")
    plt.title("Répartition des Niveaux de Risque (0.0 à 3.0)")
    plt.xticks(rotation=0)
    plt.tight_layout()
    st.pyplot(fig_sech_maison_dist)


with col2_maison_sech_box:
    st.markdown("##### Box Plot : Prix au $m^2$ Terrain en fonction du Risque Sécheresse")

    df_maison_sech_filtered = df_resultat_maison[df_resultat_maison["valeur_fonciere_par_surf"] < 1.5e3]

    fig6 = plt.figure(figsize=(10, 6))
    sns.boxplot(
        x='zone_niveau', 
        y='valeur_fonciere_par_surf', 
        data=df_maison_sech_filtered,
        order=[0.0, 1.0, 2.0, 3.0], 
        palette=['#4CAF50', '#FFC107', '#F44336', '#B71C1C']
    )
    plt.title('Distribution du Prix/m² Terrain par Niveau de Risque Sécheresse (Maisons)')
    plt.xlabel('Niveau de Risque Sécheresse (0.0: Très Faible, 3.0: Très Fort)')
    plt.ylabel('Prix au $m^2$ Terrain (Valeur Foncière / Surface Terrain)')
    plt.xticks(rotation=0)
    plt.tight_layout()
    st.pyplot(fig6)