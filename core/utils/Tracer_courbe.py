import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def graph(fichier_blanc, fichier_echantillon, Nom_echantillon, Titre, chemin): # fichier_blanc, fichier_echantillon: (str) Chemin d'accès des fichiers créés pour l'expérience 
    data_1 = pd.read_csv(fichier_blanc,  encoding='ISO-8859-1')
    data_2= pd.read_csv(fichier_echantillon,  encoding='ISO-8859-1')
# Obtenir les colonnes 'Longueur d\'onde' et Tension Blanc et Tension échantillon
    Longueur_donde = data_1['Longueur d\'onde (nm)']
    Tension_blanc = data_1['Tension blanc (Volt)']
    Tension_echantillon= data_2['Tension échantillon (Volt)']
    Absorbance=np.log10(np.abs(Tension_blanc)/np.abs(Tension_echantillon))
    Pic_d_absorbance=max(Absorbance)
    Pic_longueur_donde=Longueur_donde[np.argmax((Absorbance))]

# Création du graphique
    plt.plot(Longueur_donde, Absorbance)
    plt.xlabel('Longueur d\'onde (nm)')
    plt.ylabel('Absorbance')
    plt.title('Absorbance du '+ Nom_echantillon)

# Mise en évidence du point de pic en rouge
    plt.scatter(Pic_longueur_donde, Pic_d_absorbance, color='red')


# Annotation des coordonnées du point
    plt.annotate('({:.2f} nm, {:.2f})'.format(Pic_longueur_donde, Pic_d_absorbance),
             xy=(Pic_longueur_donde , Pic_d_absorbance),
             xytext=(Pic_longueur_donde + 10 , Pic_d_absorbance),
             fontsize=10,
             color='red',
             arrowprops=dict(facecolor='red', arrowstyle='->'))

# Ligne pointillée reliant le point de pic à l'axe des x
    plt.hlines(y=Pic_d_absorbance, xmin=Longueur_donde[0] , xmax=Pic_longueur_donde, linestyle='dashed', color='red')

# Ligne pointillée reliant le point de pic à l'axe des y
    plt.vlines(x=Pic_longueur_donde, ymin=min(Absorbance), ymax=Pic_d_absorbance, linestyle='dashed', color='red')
# Affichage du graphique
    plt.savefig(chemin +'\\'+ Titre+".pdf")

    plt.show()
