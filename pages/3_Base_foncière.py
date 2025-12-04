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
    page_title="Présentation du jeu de données des valeurs foncières",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. TITRE ET INTRODUCTION ---
st.title("Présentation du jeu de données des valeurs foncières 🏠📊")

st.markdown("""
Voici une première visualisation du contenu du jeu de données des valeurs foncières.
""")