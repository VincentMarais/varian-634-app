import serial  
import numpy as np
import time # bibliothèque temps 
import numpy as np
from pyfirmata import Arduino, util

from core.kinematic_chains.screw_motor import state_screw_motor, grbl_parameter_screw_motor, initialisation_motor_screw, move_screw, return_screw
from core.kinematic_chains.mirror_cuves_motor import move_mirror_cuves_motor , initialisation_mirror_cuves_motor
from core.kinematic_chains.end_stop_sensor import *

from core.electronics_controler.ni_pci_6621 import acquisition_tension

from core.utils.Enregistrement_des_fichiers import save_data_csv
from core.utils.Tracer_courbe import graph
from core.utils.Creation_repertoire import creation_repertoire_date_slot 

"""
Initialisation fichier pour le programme 
"""
[REPERTORY, DATE, SLOT_SIZE] = creation_repertoire_date_slot()



"""
INITIALISATION DE L'ARDUINO + CARTE NI-PCI 6221
"""

# Initialisation carte NI-PCI 6221
PULSE_FREQUENCY = np.array([20.0]) # 20Hz l'amplitude de la tension est maximale aux bornes de la photodiode, si on augmente la fréquence aux bornes de la photodiode => diminution de la tension
DUTY_CYCLE = np.array([0.5]) # Déterminer un rapport cyclique optimal pour la mesure
SAMPLES_PER_CHANNEL = 30000 # Nombre d'échantillon récupéré
SAMPLE_RATE = 250000 # Fréquence d'échantillonage maximale de la carte (on récupère une partie du signal cf critère de Shannon)
CHANNELS = ['Dev1/ai0', 'Dev1/ai1']  

# INITIALISATION ARDUINO MOTEURS
COM_PORT = 'COM3'
BAUD_RATE = 115200
INITIALIZATION_TIME = 2
S = serial.Serial(COM_PORT, BAUD_RATE)
S.write("\r\n\r\n".encode()) # encode pour convertir "\r\n\r\n" 
time.sleep(INITIALIZATION_TIME)   # Attend initialisation un GRBL
S.flushInput()  # Vider le tampon d'entrée, en supprimant tout son contenu.


# INITIALISATION ARDUINO Fourche OPTIQUE
BOARD_OPTICAL_FORK = Arduino('COM8')
it = util.Iterator(BOARD_OPTICAL_FORK)
it.start()
PIN = BOARD_OPTICAL_FORK.get_pin('d:3:i')  # d pour digital, 3 pour le pin 3, i pour input



"""
ACQUISITION DU SIGNAL
"""
def mode_precision(course_vis, nombre_de_mesures, vitesse_translation_vis):  # d: distance parcourue par la vis en mm/  n: nombre de mesure de tension / vitesse_translation_vis: vitesse_translation_vis translation de la vis (mm/min)
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
    initialisation_mirror_cuves_motor(S,PIN)

    initialisation_motor_screw(S,vitesse_translation_vis)
    
    


    """
    Début de l'acquisition
    """
    while i < course_vis: # Tant que la vis n'a pas parcouru une distance course_vis
        Tension_capteur_1 = acquisition_tension(PULSE_FREQUENCY, DUTY_CYCLE, 'ai0')
        Tensions_capteur_1.append(Tension_capteur_1)

        move_mirror_cuves_motor(S, 0.33334)  # Le moteur doit faire une angle de 60°
        time.sleep(0.5)
        
        Tension_capteur_2 = acquisition_tension(PULSE_FREQUENCY, DUTY_CYCLE, 'ai1')
        Tensions_capteur_2.append(Tension_capteur_2)

        move_mirror_cuves_motor(S, -0.33334)  # Le moteur doit faire une angle de 60°
        time.sleep(0.5)

        pas_de_vis.append(i)
        Longueur_d_onde.append(-31.10419907 * i + 800)  # cf rapport 2022-2023 dans la partie "Acquisition du signal"

        move_screw(S, i + pas)  # Le moteur travail en mode absolu par défaut G90

        print(f"Tension photodiode 1 (Volt) : {Tensions_capteur_1}")
        print(f"Taille de la liste Tension photodiode 1 : {len(Tensions_capteur_1)}")
        print(f"Tension photodiode 2 (Volt) : {Tensions_capteur_2}")
        print(f"Taille de la liste photodiode 2 : {len(Tensions_capteur_2)}")
        print(f"Pas de vis (mm) : {i}")
        print(f"Longueur d'onde (nm) : {Longueur_d_onde}")
        print(f"Taille de la liste Longueur d'onde (nm) : {len(Longueur_d_onde)}")

        time.sleep(temps_par_pas)  # Comme $110 =4mm/min et le pas de vis est de 0.5mm => Le moteur réalise un pas de vis en 7.49s
        i += pas

        
        

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
def ACQUISITION(course_vis, nombre_de_mesure, vitesse_translation_vis, PULSE_FREQUENCY, DUTY_CYCLE, fichier_blanc, fichier_echantillon, Nom_echantillon, Titre, REPERTORY): # Départ 7.25mm / 21 - 7.25 = 13.75mm où 21 course de la vis total de la vis => course_vis=13.75mm
    nom_colonne_tension_blanc='Tension blanc (Volt)'

    nom_colonne_tension_echantillon='Tension échantillon (Volt)'

   
  


    [Longueur_d_onde, Tension_blanc, Tension_echantillon, pas_de_vis] = mode_precision(course_vis, nombre_de_mesure, vitesse_translation_vis, PULSE_FREQUENCY, DUTY_CYCLE)
    

   

    

    
    save_data_csv(fichier_echantillon, Longueur_d_onde, Tension_echantillon, pas_de_vis, 'Longueur d\'onde (nm)', nom_colonne_tension_echantillon,'Liste_pas_vis')
    save_data_csv(fichier_blanc, Longueur_d_onde, Tension_blanc, pas_de_vis, 'Longueur d\'onde (nm)', nom_colonne_tension_blanc,'Liste_pas_vis')

    a=str(state_screw_motor(S))
    while 'Idle' not in a: # 'Idle': Instruction GRBL pour dire que ce moteur est à l'arrêt / 'Run' le moteur tourne
        a=str(state_screw_motor(S))

    print(a)
    
    grbl_parameter_screw_motor(S)
    return_screw(S,course_vis, vitesse_translation_vis=10)
    grbl_parameter_screw_motor(S)    

    graph(fichier_blanc, fichier_echantillon, Nom_echantillon, Titre, REPERTORY)




"""
LANCEMENT DU PROGRAMME
"""

# Concaténer les variables pour former le chemin d'accès complet




course_vis=2 # 7mm
nombre_de_mesures=10 # A modifier si on veut être plus précis
vitesse_translation_vis=10 # mm/min

Nom_echantillon=input("Nom de l'échantillon :") # A modifier si on change de composé chimique


fichier_blanc=  REPERTORY + '\Tension_blanc_' + DATE + "_" + SLOT_SIZE + '.csv'
fichier_echantillon=  REPERTORY + '\Tension_echantillon_' + DATE + "_" + SLOT_SIZE + '.csv'


Titre="Absorbance_"+ "_" + Nom_echantillon+ DATE+"_"+ SLOT_SIZE  

ACQUISITION(course_vis, nombre_de_mesures, vitesse_translation_vis, PULSE_FREQUENCY, DUTY_CYCLE, fichier_blanc, fichier_echantillon, Nom_echantillon, Titre, REPERTORY) # course_vis 13.75 mm / 260 points / vitesse_translation_vis = 4mm/min
#graph(fichier_blanc, fichier_echantillon, Nom_echantillon, Titre, REPERTORY)

#mode_precision(course_vis, nombre_de_mesures, vitesse_translation_vis, Frequence_creneau=np.array([Frequence_creneau]), DUTY_CYCLE=np.array([DUTY_CYCLE]))

