import streamlit as st
import pandas as pd # Import pour éviter les erreurs si des fonctions globales sont appelées

# ***************************************************************
# 1. Configuration de la Page et Contenu
# ***************************************************************

st.set_page_config(
    page_title="Accueil Sykinet Aléa",
    layout="centered", 
    initial_sidebar_state="expanded"
)

st.title("🏡 Bienvenue sur notre page de visualisation de données Sykinet")
st.markdown("---")

st.info("Notre problématique est la recherche d'un lien entre les bâtiments résidentiels (maisons et appartements) et les risques de sécheresse et d'inondation sur leur terrain.")

st.header("Sommaire")
st.markdown("""
- **Analyse des données climatiques :** Visualisation des risques d'inondation (débordements de nappe, inondations de cave) et de sécheresse.
- **Cartes Interactives :** Pour chaque département, nous pouvons visualiser leur situation en terme de risques d'inondation et de sécheresse.
- **Analyse des données de valeurs foncière :** Analyse des données sur la France entière.
- **Mise en relation des données d'inondation et de sécheresse avec les valeurs foncières :** recherche d'un lien quantitatif entre les données.            
""")

st.markdown("---")
# L'interface multi-page de Streamlit crée automatiquement un lien vers la page "Cartographie"
# dans la barre latérale gauche.

st.subheader("Naviguer entre les onglets")

st.markdown("""
Utilisez la barre latérale pour naviguer entre les pages de l'application.
""")

# Un message d'aide simple dans la barre latérale
with st.sidebar:
    st.header("Auteurs")
    st.success("Les auteurs sont : Sylviane ANDRIAMANANA, Kindak DIKONGUE, Etienne LEFEBVRE")