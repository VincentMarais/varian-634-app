import serial  
import numpy as np
import time # bibliothèque temps 
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy as np
from pyfirmata import Arduino, util
from Utilitaires.Creation_repertoire import Repertoire_Date_Fente 
from Fonctions_commande_moteur.Fonction_code_moteur import etat_mot, param_mot, deplacer_vis, retour_moteur_vis, deplacer_moteur_miroir
from Fonctions_commande_moteur.Fonction_fourche_optique import fourche_optique_etat
from Carte_NI_PCI.Acquisition_Tension_NI_6621 import acquisition_tension
from Utilitaires.Enregistrement_des_fichiers import sauvegarder_donnees
from Utilitaires.Tracer_courbe import graph
"""
Initialisation fichier pour le programme 
"""
[chemin, Date, Taille_de_fente] = Repertoire_Date_Fente()



"""
INITIALISATION DE L'ARDUINO + CARTE NI-PCI 6221
"""

Frequence_creneau = np.array([20.0]) # 20Hz l'amplitude de la tension est maximale aux bornes de la photodiode, si on augmente la fréquence aux bornes de la photodiode => diminution de la tension
Rapport_cyclique = np.array([0.5]) # Déterminer un rapport cyclique optimal pour la mesure
SAMPLES_PER_CHANNEL = 30000 # Nombre d'échantillon récupéré
SAMPLE_RATE = 250000 # Fréquence d'échantillonage maximale de la carte (on récupère une partie du signal cf critère de Shannon)
CHANNELS = ['Dev1/ai0', 'Dev1/ai1']  

# Constantes ARDUINO MOTEUR
COM_PORT = 'COM3'
BAUD_RATE = 115200
INITIALIZATION_TIME = 2
# Initialisation arduino
S = serial.Serial(COM_PORT, BAUD_RATE)
S.write("\r\n\r\n".encode()) # encode pour convertir "\r\n\r\n" 
time.sleep(INITIALIZATION_TIME)   # Attend initialisation un GRBL
S.flushInput()  # Vider le tampon d'entrée, en supprimant tout son contenu.


# Constantes ARDUINO Fourche OPTIQUE
board = Arduino('COM8')
it = util.Iterator(board)
it.start()
PIN = board.get_pin('d:3:i')  # d pour digital, 3 pour le pin 3, i pour input



"""
ACQUISITION DU SIGNAL
"""


def mode_precision(course_vis, nombre_de_mesures, vitesse_translation_vis, Frequence_creneau, Rapport_cyclique):  # d: distance parcourue par la vis en mm/  n: nombre de mesure de tension / vitesse_translation_vis: vitesse_translation_vis translation de la vis (mm/min)
    """
    Entrée :

    Sortie : 
    
    """
    
    Tensions_capteur_1= []
    Tensions_capteur_2= []

    Longueur_d_onde=[]
    pas_de_vis=[]
    i=0
    pas=course_vis/nombre_de_mesures # 0.5mm Pas de la vis (cf Exel)
    temps_par_pas= (pas*60)/vitesse_translation_vis # Temps pour faire un pas 
    
    """
    Initialisation moteur    
    """
    a=fourche_optique_etat(PIN)
    print(a)
    if a!='Bonne photodiode':
        while a!='Bonne photodiode':
            a=fourche_optique_etat(PIN)
            if a=='Mauvaise photodiode':
                print("TOURNE 60° car :", a)                  
                deplacer_moteur_miroir(S,0.4) # Le moteur doit faire une angle de 60°                 
                time.sleep(1)
                a=fourche_optique_etat(PIN)
                print("TOURNE -60° car :", a)
                deplacer_moteur_miroir(S,-0.4) # Le moteur doit faire une angle de 60° 

            else:
                print(a)

        else: 
            print(a)
    g_code= 'G90'+ '\n' # Le moteur se déplace en relatif
    S.write(g_code.encode())
    time.sleep(0.5)

    g_code= '$110=' + str(vitesse_translation_vis) + '\n'
    S.write(g_code.encode())
    time.sleep(0.5)


    """
    Début : De l'acquisition
    """
    while i < course_vis: # Tant que la vis n'a pas parcouru une distance course_vis

        Tension_capteur_1=acquisition_tension(Frequence_creneau, Rapport_cyclique, 'ai0' )
        Tensions_capteur_1.append(Tension_capteur_1) # 
        print("Tension photodiode 1 (Volt) :", Tensions_capteur_1)
        print("Taille de la liste Tension photodiode 1 :", len(Tensions_capteur_1))

        deplacer_moteur_miroir(S,0.33334) # Le moteur doit faire une angle de 60° 
        time.sleep(0.5)
        Tension_capteur_2=acquisition_tension(Frequence_creneau, Rapport_cyclique, 'ai1' )
        Tensions_capteur_2.append(Tension_capteur_2) # 
        print("Tension photodiode 2 (Volt) :",Tensions_capteur_2)
        print("Taille de la liste photodiode 2 :", len(Tensions_capteur_2))

        deplacer_moteur_miroir(S,-0.33334) # Le moteur doit faire une angle de 60° 
        time.sleep(0.5)

        pas_de_vis.append(i)
        Longueur_d_onde.append(-31.10419907*i +800) # Je suppose que l'on part à 400nm -> 5.4mm et que l'on fini à 800 nm --> 18.73nm
        
        deplacer_vis(S,i+pas) # Le moteur travail en mode absolu par défaut G90 
        
        print("Pas de vis (mm) :", i)     
        print("Longueur d\'onde (nm) :", Longueur_d_onde)
        print("Taille de la liste Longueur d\'onde (nm) :", len(Longueur_d_onde))
        
        time.sleep(temps_par_pas) # Comme $110 =4mm/min et le pas de vis est de 0.5mm => Le moteur réalise un pas de vis en 7.49s
        i+=pas
        

    """
    Fin de l'acquisition
    """

   
    Longueur_d_onde.reverse()
    Tensions_capteur_1.reverse()
    Tensions_capteur_2.reverse()
    pas_de_vis.reverse()

    return  Longueur_d_onde, Tensions_capteur_1, Tensions_capteur_2, pas_de_vis




"""
PARTIE ACQUISITION DES DONNEES
""" 
def ACQUISITION(course_vis, nombre_de_mesure, vitesse_translation_vis, Frequence_creneau, Rapport_cyclique, fichier_blanc, fichier_echantillon, Nom_echantillon, Titre, chemin): # Départ 7.25mm / 21 - 7.25 = 13.75mm où 21 course de la vis total de la vis => course_vis=13.75mm
    nom_colonne_tension_blanc='Tension blanc (Volt)'

    nom_colonne_tension_echantillon='Tension échantillon (Volt)'

   
  


    [Longueur_d_onde, Tension_blanc, Tension_echantillon, pas_de_vis] = mode_precision(course_vis, nombre_de_mesure, vitesse_translation_vis, Frequence_creneau, Rapport_cyclique)
    

   

    

    
    sauvegarder_donnees(fichier_echantillon, Longueur_d_onde, Tension_echantillon, pas_de_vis, 'Longueur d\'onde (nm)', nom_colonne_tension_echantillon,'Liste_pas_vis')
    sauvegarder_donnees(fichier_blanc, Longueur_d_onde, Tension_blanc, pas_de_vis, 'Longueur d\'onde (nm)', nom_colonne_tension_blanc,'Liste_pas_vis')

    a=str(etat_mot(S))
    while 'Idle' not in a: # 'Idle': Instruction GRBL pour dire que ce moteur est à l'arrêt / 'Run' le moteur tourne
        a=str(etat_mot(S))

    print(a)
    
    param_mot(S)
    retour_moteur_vis(S,course_vis, vitesse_translation_vis=10)
    param_mot(S)    

    graph(fichier_blanc, fichier_echantillon, Nom_echantillon, Titre, chemin)




"""
LANCEMENT DU PROGRAMME
"""

# Concaténer les variables pour former le chemin d'accès complet




course_vis=2 # 7mm
nombre_de_mesures=10 # A modifier si on veut être plus précis
vitesse_translation_vis=10 # 4mm/min

Nom_echantillon=input("Nom de l'échantillon :") # A modifier si on change de composé chimique


fichier_blanc=  chemin + '\Tension_blanc_' + Date + "_" + Taille_de_fente + '.csv'
fichier_echantillon=  chemin + '\Tension_echantillon_' + Date + "_" + Taille_de_fente + '.csv'


Titre="Absorbance_"+ "_" + Nom_echantillon+ Date+"_"+ Taille_de_fente  

ACQUISITION(course_vis, nombre_de_mesures, vitesse_translation_vis, Frequence_creneau, Rapport_cyclique, fichier_blanc, fichier_echantillon, Nom_echantillon, Titre, chemin) # course_vis 13.75 mm / 260 points / vitesse_translation_vis = 4mm/min
#graph(fichier_blanc, fichier_echantillon, Nom_echantillon, Titre, chemin)

#mode_precision(course_vis, nombre_de_mesures, vitesse_translation_vis, Frequence_creneau=np.array([Frequence_creneau]), Rapport_cyclique=np.array([Rapport_cyclique]))

