import streamlit as st
import pandas as pd
from st_files_connection import FilesConnection 
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import plotly.express as px
# Note: geopandas et shapely ne sont pas utilisés dans ce code, mais gardés pour l'exhaustivité
# import geopandas as gpd
# from shapely import wkt

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
df_doublons = conn.read(path + "df_doublons.csv", input_format="csv")
diff_locaux = conn.read(path + "differents_locaux.csv", input_format="csv")
nature_mutations = conn.read(path + "nature_mutation.csv", input_format="csv")


# --- 4. RENOMMER ET VÉRIFIER LES COLONNES (Hypothèse: Colonnes 0 et 1) ---
# Si vos DataFrames n'ont pas d'en-tête, le nom par défaut sera 0 et 1. 
# Si vos DataFrames ont des noms, remplacez 0 et 1 par les noms réels.

# Doublons
df_doublons.columns = ['Statut', 'Nombre_Transactions']
# Locaux
diff_locaux.columns = ['Type_Local', 'Nombre_Transactions']
# Mutations
nature_mutations.columns = ['Nature_Mutation', 'Nombre_Transactions']


# ==============================================================================
# SECTION DES GRAPHIQUES CAMEMBERTS
# ==============================================================================
st.header("Analyse de la Répartition des Données Clés 🍰")
st.markdown("---")

col_d, col_l, col_m = st.columns(3)

# Graphique 1 : Doublons
with col_d:
    st.subheader("Répartition des Doublons")
    try:
        fig_doublons = px.pie(
            df_doublons, 
            values='Nombre_Transactions', 
            names='Statut', 
            title='Statut des Observations'
        )
        # Affichage du pourcentage et de l'étiquette à l'intérieur du camembert
        fig_doublons.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_doublons, use_container_width=True)
    except Exception as e:
        st.error(f"Erreur lors de la création du graphique Doublons. Vérifiez les noms de colonnes. Erreur: {e}")


# Graphique 2 : Locaux
with col_l:
    st.subheader("Types de Locaux")
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
        st.error(f"Erreur lors de la création du graphique Locaux. Vérifiez les noms de colonnes. Erreur: {e}")


# Graphique 3 : Mutations
with col_m:
    st.subheader("Nature des Mutations")
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
        st.error(f"Erreur lors de la création du graphique Mutations. Vérifiez les noms de colonnes. Erreur: {e}")