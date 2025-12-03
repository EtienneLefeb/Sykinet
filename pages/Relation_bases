import streamlit as st
import geopandas as gpd
import pandas as pd
from shapely import wkt
from st_files_connection import FilesConnection  # Import nécessaire pour la connexion GCS
import matplotlib.pyplot as plt
import numpy as np
from io import StringIO
import seaborn as sns



st.set_page_config(
    page_title="Mise en relation des risques climatiques et des valeurs foncières",
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.title("Mise en relation des risques climatiques et des valeurs foncières")
st.markdown("""
La base de données des valeurs foncières est très complète,
nous avons choisi de nous concentrer sur une base ne contenant que les ventes d'appartements et une autre base ne contenant que des ventes de maisons. 
Ces bases nous les avons réduites aux régions de Nouvelle Aquitaine, d'Occitanie et de Centre-Val de Loire, où dans chaque département, les risques sécheresse et inondations sont présents.
""")

path = "streamlit-sykinet/base sykinet/"
conn = st.connection("gcs", type=FilesConnection) 
df_resultat_innond_final = conn.read(path + "base_innond_final.csv", input_format="csv")    


counts = df_resultat_innond_final['Risque_innond'].value_counts()

# Création du graphique
fig = plt.figure(figsize=(6,4))
counts.plot(kind='bar')

plt.xlabel("Risque d'inondation")
plt.ylabel("Nombre de cas")
plt.title("Répartition des modalités de Risque_inondonations")
plt.tight_layout()
st.pyplot(fig)

x_0 = df_resultat_innond_final[df_resultat_innond_final["Risque_innond"]=="Pas de débordement de nappe ni d'inondation de cave"]["surface_reelle_bati"]
y_0 = df_resultat_innond_final[df_resultat_innond_final["Risque_innond"]=="Pas de débordement de nappe ni d'inondation de cave"]["valeur_fonciere"]

x_cave = df_resultat_innond_final[df_resultat_innond_final["Risque_innond"]=='Zones potentiellement sujettes aux inondations de cave']["surface_reelle_bati"]
y_cave = df_resultat_innond_final[df_resultat_innond_final["Risque_innond"]=='Zones potentiellement sujettes aux inondations de cave']["valeur_fonciere"]

x_nappe = df_resultat_innond_final[df_resultat_innond_final["Risque_innond"]=='Zones potentiellement sujettes aux débordements de nappe']["surface_reelle_bati"]
y_nappe = df_resultat_innond_final[df_resultat_innond_final["Risque_innond"]=='Zones potentiellement sujettes aux débordements de nappe']["valeur_fonciere"]

fig2 = plt.figure()
plt.scatter(x_0 , y_0 , color = '#4CAF50',label = "Pas de risque")
plt.scatter(x_cave , y_cave , color = '#2196F3',alpha = 0.5,label="Inondations de cave",marker ="*")
plt.scatter(x_nappe , y_nappe , color = '#FFC107' , alpha = 0.3, label = "debordements de nappes",marker = "+")
plt.xlim([0,400])
plt.ylim([0,1e6])
plt.legend()
st.pyplot(fig2)

df_resultat_innond_final["valeur_fonciere_par_surface"] = df_resultat_innond_final['valeur_fonciere']/df_resultat_innond_final['surface_reelle_bati']
df_resultat_innond_final = df_resultat_innond_final[~df_resultat_innond_final["Risque_innond"].isna()]

fig3 = plt.figure(figsize=(20, 6))
# Le Box Plot affiche la médiane, les quartiles et les valeurs aberrantes
sns.boxplot(
    x='Risque_innond', 
    y='valeur_fonciere_par_surface', 
    data=df_resultat_innond_final,
#    order=[0.0, 1.0, 2.0] # Assure l'ordre correct des niveaux
)
plt.title('Distribution de la Valeur Foncière par Zone Niveau (Box Plot)')
plt.xlabel('Zone Niveau (Ordinal)')
plt.ylabel('Valeur Foncière par unité de surface (Quantitative)')
plt.ylim([0,1e4])
st.pyplot(fig3)
