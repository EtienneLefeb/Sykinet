import streamlit as st
import pandas as pd
from st_files_connection import FilesConnection 
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import plotly.express as px

# --- 1. CONFIGURATION DE PAGE ---
st.set_page_config(
    page_title="Présentation du jeu de données des valeurs foncières",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. TITRE ET INTRODUCTION ---
st.title("Présentation du jeu de données des valeurs foncières 🏠📊")

st.markdown("""
Voici une première visualisation du contenu du jeu de données des valeurs foncières.
""")

path = "streamlit-sykinet/base sykinet/"
conn = st.connection("gcs", type=FilesConnection)

# --- 3. CHARGEMENT DES DONNÉES ---
df_doublons_raw = conn.read(path + "df_doublons.csv", input_format="csv")
diff_locaux = conn.read(path + "differents_locaux.csv", input_format="csv")
nature_mutations = conn.read(path + "nature_mutation.csv", input_format="csv")


# --- 4. PRÉPARATION ET TRANSFORMATION DES DONNÉES ---

# 4a. TRANSFORMATION DE df_doublons (Structure: Colonnes = Catégories)
if df_doublons_raw.shape[0] == 1:
    df_doublons = df_doublons_raw.T.reset_index()
    # On suppose que la première ligne de l'index transposé est l'ancienne tête de colonne
    df_doublons.columns = ['Statut', 'Nombre_Transactions']
else:
    st.warning("Le format de 'df_doublons' n'est pas une seule ligne avec des catégories en colonnes. Utilisation du format simple à deux colonnes.")
    df_doublons = df_doublons_raw.copy()
    df_doublons.columns = ['Statut', 'Nombre_Transactions']


# 4b. RENOMMAGE pour diff_locaux et nature_mutations (Structure: 2 colonnes)
diff_locaux.columns = ['Type_Local', 'Nombre_Transactions']
nature_mutations.columns = ['Nature_Mutation', 'Nombre_Transactions']


# ==============================================================================
# SECTION DES GRAPHIQUES CAMEMBERTS
# ==============================================================================
st.header("Analyse de la Répartition des Données Clés 🍰")
st.markdown("---")

col_d, col_l, col_m = st.columns(3)

# Graphique 1 : Doublons (Utilisation du DataFrame transformé)
with col_d:
    st.subheader("1. Répartition des Doublons")
    try:
        fig_doublons = px.pie(
            df_doublons, 
            values='Nombre_Transactions', 
            names='Statut', 
            title='Statut des Observations'
        )
        fig_doublons.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_doublons, use_container_width=True)
    except Exception as e:
        st.error(f"Erreur lors de la création du graphique Doublons. Erreur: {e}")


# Graphique 2 : Locaux
with col_l:
    st.subheader("2. Types de Locaux")
    try:
        fig_locaux = px.pie(
            diff_locaux, 
            values='Nombre_Transactions', 
            names='Type_Local', 
            title='Distribution des Types de Locaux'
        )
        fig_locaux.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_locaux, use_container_width=True)
    except Exception as e:
        st.error(f"Erreur lors de la création du graphique Locaux. Erreur: {e}")


# Graphique 3 : Mutations
with col_m:
    st.subheader("3. Nature des Mutations")
    try:
        fig_mutations = px.pie(
            nature_mutations, 
            values='Nombre_Transactions', 
            names='Nature_Mutation', 
            title='Nature des Transactions'
        )
        fig_mutations.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_mutations, use_container_width=True)
    except Exception as e:
        st.error(f"Erreur lors de la création du graphique Mutations. Erreur: {e}")


# ==============================================================================
# SECTION D'ANALYSE (Nouvelle structure)
# ==============================================================================
st.divider()
st.header("Analyse et Choix Méthodologiques 🎯")

# Utilisation d'un conteneur pour une meilleure séparation visuelle
with st.container(border=True):
    st.markdown("""
    Pour notre analyse de l'impact des risques climatiques, nous avons dû affiner les données brutes des valeurs foncières.
    
    ### 1. Filtrage sur les Transactions (Graphique 1 & 3)
    
    * **Unicité du Local (Doublons) :** Afin d'obtenir le prix foncier d'un **bâtiment unique**, nous avons filtré les transactions qui ne concernent qu'un seul local. Cette étape est cruciale pour une évaluation précise, mais elle a entraîné une perte significative des données brutes (environ **86% des lignes**).
    * **Nature de la Mutation :** Nous avons choisi de nous concentrer sur les **ventes (Vente)**, car elles représentent de loin la grande majorité des transactions de la base, garantissant ainsi une bonne représentativité du marché.

    ### 2. Concentration sur le Type de Local (Graphique 2)
    
    * **Focus de l'Étude :** Notre étude se concentre sur les **maisons** et les **appartements**, qui sont les types de locaux les plus sensibles aux aléas climatiques étudiés (RGA, inondations).
    * **Pistes Futures :** Un travail ultérieur pourrait être mené pour explorer l'impact sur d'autres types de biens comme les locaux industriels, les dépendances ou les terrains à bâtir.
    
    Ces choix méthodologiques nous permettent de travailler sur une base plus pertinente pour répondre à notre question principale.
    """)