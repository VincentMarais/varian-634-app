import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import find_peaks # https://www.youtube.com/watch?v=1SvDZPvUo_I&ab_channel=KiyonoLab (Vidéo sur savgol_Filter)
from scipy.interpolate import UnivariateSpline
import os
import datetime
import matplotlib.animation as animation
from matplotlib import style
#CONSTANTE
FE = 250000 # Fréquence d'échantillonage de la carte NI-PCI 6221
"""
VARIABLES
"""


Fenetre_recherche_pic = 25 # Définir la largeur de la fenêtre de recherche des pics (25 pour 0.2mm)
Largeur_fonction_porte = 35 # reglage opti (Fente 0_2mm): 23 / (Fente 0_5mm): 30 / (Fente 1mm): 15 / (Fente 2mm): 30 (# Définir la taille de la fenêtre de lissage)


"""
INITIALISATION DE LA MANIP
"""

CHEMIN="C:\\Users\\admin\\Documents\\Projet_GP\\Programmation_Spectro\\Programmation_application_spectro\\Manip\\Manip_2023\\Manip_06_2023\\30_06_2023\\Fente_2nm"
Date="30_06_2023"
Taille_de_fente = "Fente_2_nm"
nom_espece_chimique=input("Qu'elle est votre échantillon étudié :")

"""
Lecture des fichier csv créé lors de l'acquisition 
"""


fichier_blanc=  CHEMIN + '\\'+ "Tension_blanc_30_06_2023_Fente_2nm.csv"
fichier_echantillon=  CHEMIN + '\\' + "Tension_echantillon_30_06_2023_Fente_2nm.csv"


data_solution_blanc = pd.read_csv(fichier_blanc, encoding='ISO-8859-1')
data_solution_echantillon= pd.read_csv(fichier_echantillon, encoding='ISO-8859-1')
#data_bruit_de_noir=pd.read_csv(Chemin_acces +'\Tension_de_noir_31_03_2023.csv', encoding='ISO-8859-1')




# Obtenir les colonnes 
Longueur_donde = data_solution_echantillon['Longueur d\'onde (nm)']
Tension_blanc = data_solution_blanc['Tension blanc (Volt)']
Tension_echantillon= data_solution_echantillon['Tension échantillon (Volt)']





"""
Correction préliminaire du signal
"""
def creaction_de_chemin(Grandeur_physique):
    chemin = os.path.join(CHEMIN, Grandeur_physique)

    if not os.path.exists(chemin):
    # Créer le répertoire en utilisant le chemin d'accès
        os.makedirs(chemin)
        print("Répertoire créé avec succès :", chemin)
    else:
        print("Le répertoire existe déjà :", chemin)

    return chemin


# Supprimmer le bruit de noir
def correction_bruit_de_noir(Absorbance_noir,Absorbance_solution):
    """
    Entrée : 
        - Absorbance_noir (liste) : L'absorbance de noir est l'absorbance mesurée pour chaque longueur d'onde avec 
        une largeur de fente donnée. Lorsqu'il n'y a pas de cuve, l'absorbance mesurée doit être nulle si :

            L'intensité lumineuse mesurée sur la photodiode 1 = l'intensité lumineuse mesurée sur la photodiode 2. 
         
        Cependant, étant donné que les capteurs sont différents, L'absorbance de noir n'est pas nulle pour toute les longueur d'onde.


        - Absorbance_solution (liste) : Absorbance_solution est l'absorbance mesurée pour chaque longueur d'onde avec 
        une largeur de fente donnée. Lorqu'il y a les deux cuves avec des solutions à l'intérieurs.

    Sortie :

        - Absorbance_corrige (liste) : Absorbance où l'on a supprimer l'absorbance de noir pour chaque longueur d'onde.

    BUT : Avoir des valeurs cohérente d'absorbances de notre solution pour chaque longueur d'onde.
    """
    pass



# Supprimer les absorbances négatives 
def correction_absorbance_negative(Tension_blanc, Tension_echantillon):
    """
    Entrée : 
        - Tension_blanc (liste) : Liste des tensions mesurer aux bornes de la photodiode où il y a la cuve de la solution de blanc.

        - Tension_echantillon (liste) : Liste des tensions mesurer aux bornes de la photodiode où il y a la cuve de l'échantillon.

    Sortie :
        - Tension_blanc (liste) : Liste des tensions mesurer aux bornes de la photodiode où il y a la cuve de la solution de blanc.

        - Tension_echantillon (liste) : Liste des tensions mesurer aux bornes de la photodiode où il y a la cuve de l'échantillon corrigé, 
        c'est à dire que pour toute Tension_echantillon[i] et Tension_blanc[i] on a :
                                Tension_echantillon[i] =< Tension_blanc[i]
        
    BUT : Supprimer les absorbance négative pour être en accord avec la réalité physique de notre solution 
    (cf Rapport 2022-2023 pour plus de détaille sur la physique du problème)
-
    """
    for i in range (len(Tension_blanc)):

        if np.abs(Tension_blanc[i]) < np.abs(Tension_echantillon[i]): # Ce qui est possible s'il y a du bruit de mesure 
            Tension_echantillon[i]=Tension_blanc[i]

    return Tension_blanc, Tension_echantillon


def zero_absorbance(Absorbance_spline):
    """
    Entrée : 
        - Absorbance_spline (liste) : Absorbance calculer après lui avoir appliqué un spline cubique

    Sortie: Absorbance_spline (liste) : Absorbance calculer après lui avoir appliqué un spline cubique corrigé, c'est à dire :

                                            Pour tout i, Absorbance_spline[i] >= 0
    
    

    BUT : Supprimer les absorbance négative pour être en accord avec la réalité physique de notre solution 
    (cf Rapport 2022-2023 pour plus de détaille sur la physique du problème)
    """
    for i in range(len(Absorbance_spline)):
        if Absorbance_spline[i] < 0:
            Absorbance_spline[i]=0
    return Absorbance_spline


"""
AFFICHAGE PICS
"""
def Affichage_des_max_Absorbance(Pic_longueur_donde, Pic_d_absorbance, Absorbance):
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


def Affichage_courbe_Tension(Titre, Longueur_donde, Tension):
    plt.plot(Longueur_donde,Tension, color='red')
    plt.xlabel('Longueur d\'onde (nm)')
    plt.ylabel('Tension (Volt)')
    plt.title(Titre)
    chemin = creaction_de_chemin('Tension')
    plt.savefig(chemin + "\\" + Titre+".pdf")
    plt.show()

def Affichage_Transformee_de_Fourier(Titre, Tension):
    fourier_transform = np.fft.fft(Tension,n=4096) # 4096 Pour plus de précision fft (zero padding) cf https://www.youtube.com/watch?v=LAswxBR513M&t=582s&ab_channel=VincentChoqueuse
    f=FE*np.arange(4096)/4096  # Liste des fréquences de mon signal  
    fourier_transform=np.abs(fourier_transform) 
    plt.plot(f,fourier_transform, color='red')
    plt.xlabel('Fréquence (Hz)')
    plt.ylabel('Module de la transformée de Fourier')
    plt.title(Titre)
    chemin = creaction_de_chemin('Transformee_de_Fourier')
    plt.savefig(chemin + "\\" + Titre+".pdf")
    plt.show()

def Sauvegarder_pics(Titre, Absorbance):   
    peaks, _ = find_peaks(Absorbance, distance=Fenetre_recherche_pic) # La fonction find_peaks de scipy.signal permet de trouver les maxima locaux dans un signal en comparant les valeurs voisines
    chemin= creaction_de_chemin('Absorbance')

    # Affichage des pics détectés
    print('Les pics d\'absorbance se trouvent aux positions suivantes :')
    for i in peaks:
        print('{:.2f} nm : {:.2f}'.format(Longueur_donde[i], Absorbance[i]))


    # Calculer le maximum d'absorbance
    Max_absorbance = Absorbance.max()

    # Trouver la longueur lié au maximum d'absorbance 
    s = pd.Series(Absorbance)
    max_index = s.idxmax()


    fichier_peaks=  chemin + '\pic_'+Titre + "_" + Date + "_" + Taille_de_fente + '.csv'

    df = pd.DataFrame({'Longueur_d_onde_(nm)': Longueur_donde[peaks], 'Absorbance': Absorbance[peaks]})
    df.to_csv(fichier_peaks , index=False)


def Affichage_Absorbance(Titre, Absorbance):
    Pic_d_absorbance=np.max(Absorbance)
    Pic_longueur_donde=Longueur_donde[np.argmax((Absorbance))]
    # Création du graphique
    plt.plot(Longueur_donde, Absorbance)
    plt.xlabel('Longueur d\'onde (nm)')
    plt.ylabel('Absorbance')
    plt.title('Absorbance du '+ nom_espece_chimique)
    # Mise en évidence du point de pic en rouge
    Affichage_des_max_Absorbance(Pic_longueur_donde, Pic_d_absorbance, Absorbance)
    # Affichage du graphique
    chemin = creaction_de_chemin('Absorbance')
    Sauvegarder_pics(Titre, Absorbance)
    plt.savefig(chemin +'\\'+ Titre+".pdf")
    plt.show()




"""
SOLUTION DE BLANC
"""

def Generate_Affichage():
    # Affichage Tension_solution_blanc_photodiode_Lampe_XENON
    Titre="Tension_solution_blanc_photodiode_Lampe_XENON"
    Affichage_courbe_Tension(Titre, Longueur_donde, Tension=Tension_blanc)



    # Affichage Transformée_de_Fourier_solution_blanc_photodiode_Lampe_XENON
    Titre="Transformée_de_Fourier_solution_blanc_photodiode_Lampe_XENON"
    Affichage_Transformee_de_Fourier(Titre, Tension=Tension_blanc)

    # Correction de la Tension_solution_blanc_photodiode_Lampe_XENON en la convoluant avec un fonction porte  
    Tension_blanc_convolu = np.convolve(Tension_blanc, np.ones(Largeur_fonction_porte)/Largeur_fonction_porte, mode='same') # Je fais le produit de convolution de mon signal avec une  fonction porte de taille Largeur_fonction_porte

    # Affichage Tension_solution_blanc_convolue_photodiode_Lampe_XENON
    Titre="Tension_solution_blanc_convolue_photodiode_Lampe_XENON"
    Affichage_courbe_Tension(Titre, Longueur_donde, Tension=Tension_blanc_convolu)


    # Affichage Transformée_de_Fourier_solution_blanc_convolue_photodiode_Lampe_XENON
    Titre="Transformée_de_Fourier_solution_blanc_convolue_photodiode_Lampe_XENON"
    Affichage_Transformee_de_Fourier(Titre, Tension=Tension_blanc_convolu)



    """
    ECHANTILLON
    """

    # Affichage Tension_solution_echantillon_photodiode_Lampe_XENON
    Titre="Tension_solution_echantillon_photodiode_Lampe_XENON"
    Affichage_courbe_Tension(Titre, Longueur_donde, Tension=Tension_echantillon)

    # Affichage Tension_solution_blanc_photodiode_Lampe_XENON
    Titre="Transformée_de_Fourier_solution_echantillon_photodiode_Lampe_XENON"
    Affichage_Transformee_de_Fourier(Titre, Tension=Tension_echantillon)

    # Correction de la Tension_solution_echantillon_photodiode_Lampe_XENON en la convoluant avec un fonction porte  
    Tension_echantillon_convolu = np.convolve(Tension_echantillon, np.ones(Largeur_fonction_porte)/Largeur_fonction_porte, mode='same') # Je fais le produit de convolution de mon signal avec une  fonction porte de taille Largeur_fonction_porte

    Titre="Tension_solution_echantillon_convolue_photodiode_Lampe_XENON"
    Affichage_courbe_Tension(Titre, Longueur_donde, Tension=Tension_echantillon_convolu)


    # Correction de la Tension_solution_echantillon_photodiode_Lampe_XENON en la convoluant avec un fonction porte  
    Titre="Transformée_de_Fourier_solution_echantillon_convolue_photodiode_Lampe_XENON"
    Affichage_Transformee_de_Fourier(Titre, Tension=Tension_echantillon_convolu)


    """
    ABSORBANCE DE LA SOLUTION
    """



    #
    Titre="Absorbance_" + nom_espece_chimique 
    Absorbance=np.log10(np.abs(Tension_blanc)/np.abs(Tension_echantillon))
    Affichage_Absorbance(Titre, Absorbance)

    Titre="Absorbance_correction_absorbance_negative_" + nom_espece_chimique 
    Tension=correction_absorbance_negative(Tension_blanc=Tension_blanc, Tension_echantillon=Tension_echantillon)
    Absorbance_negative_correc=np.log10(np.abs(Tension[0])/np.abs(Tension[1]))
    Affichage_Absorbance(Titre, Absorbance_negative_correc)

    Titre="Absorbance_convolue_" + nom_espece_chimique  
    Absorbance_convol=np.log10(np.abs(Tension_blanc_convolu)/np.abs(Tension_echantillon_convolu))
    Affichage_Absorbance(Titre, Absorbance_convol)

    Titre="Absorbance_lisse_spline_" + nom_espece_chimique 
    spline = UnivariateSpline(Longueur_donde, Absorbance_convol, s=0.05)
    Absorbance_lisse = spline(Longueur_donde)
    Affichage_Absorbance(Titre, Absorbance_lisse)




Generate_Affichage()