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

st.title("🏡 Bienvenue sur Sykinet Aléa Cartographie")
st.markdown("---")

st.info("Cette application vous permet de visualiser les cartes d'aléa d'inondation et de sécheresse pour un département français sélectionné.")

st.header("Fonctionnalités")
st.markdown("""
- **Cartes Interactives :** Visualisation des risques d'inondation (débordements de nappe, inondations de cave) et de sécheresse.
- **Sélection par Département :** Choisissez le département pour lequel vous souhaitez analyser l'aléa.
- **Données Mises en Cache :** Chargement optimisé des données GeoPandas pour une meilleure performance.
""")

st.markdown("---")
# L'interface multi-page de Streamlit crée automatiquement un lien vers la page "Cartographie"
# dans la barre latérale gauche.

st.subheader("Accès aux Cartes")

st.markdown("""
Cliquez sur le lien **'Cartographie'** dans la barre latérale gauche pour accéder à l'outil de visualisation des cartes.
""")

# Un message d'aide simple dans la barre latérale
with st.sidebar:
    st.header("Navigation")
    st.success("Utilisez la barre latérale pour naviguer entre les pages de l'application.")