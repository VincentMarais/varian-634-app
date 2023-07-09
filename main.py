import serial  
import numpy as np
import time # bibliothèque temps 
import numpy as np
from pyfirmata import Arduino, util

from core.kinematic_chains.screw_motor import state_screw_motor, grbl_parameter_screw_motor, initialisation_motor_screw, move_screw, return_screw
from core.kinematic_chains.mirror_cuves_motor import move_mirror_cuves_motor , initialisation_mirror_cuves_motor
from core.kinematic_chains.end_stop_sensor import *

from core.electronics_controler.ni_pci_6621 import Voltage_acquisition , choice_cuvette

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
def mode_precision(screw_travel, number_measurements,screw_translation_speed):  
    """
    Entrée :
# d: distance parcourue par la vis en mm/  n: nombre de mesure de tension / screw_translation_speed: vitesse de translation de la vis (mm/min)
    Sortie : 
    
    """
    
    voltages_photodiode_1= []
    voltages_photodiode_2= []

    wavelength=[]
    no_screw=[]
    i=0
    step=screw_travel/number_measurements # 0.5mm Pas de la vis (cf Exel)
    time_per_step= (step*60)/screw_translation_speed # Temps pour faire un pas 
    

    """
    Initialisation cuves
    """
    choice = choice_cuvette()

    """
    Initialisation moteur    
    """
    initialisation_mirror_cuves_motor(S,PIN)

    initialisation_motor_screw(S,screw_translation_speed)
    

    # Hypothèse : La photodiode 1 est toujours branché sur le port 'ai0' et la photodiode 2 toujours branché sur le port 'ai1'

    """
    Début de l'acquisition
    """
    while i < course_vis: # Tant que la vis n'a pas parcouru une distance course_vis
        voltage_photodiode_1 = Voltage_acquisition(SAMPLES_PER_CHANNEL, SAMPLE_RATE, PULSE_FREQUENCY, DUTY_CYCLE, CHANNELS, solution='ai0')
        voltages_photodiode_1.append(voltage_photodiode_1)

        move_mirror_cuves_motor(S, 0.33334)  # Le moteur doit faire une angle de 60°
        time.sleep(0.5)
        
        voltage_photodiode_2 = Voltage_acquisition(SAMPLES_PER_CHANNEL, SAMPLE_RATE, PULSE_FREQUENCY, DUTY_CYCLE, CHANNELS, Channel='ai1')
        voltages_photodiode_2.append(voltage_photodiode_2)

        move_mirror_cuves_motor(S, -0.33334)  # Le moteur doit faire une angle de 60°
        time.sleep(0.5)

        no_screw.append(i)
        wavelength.append(-31.10419907 * i + 800)  # cf rapport 2022-2023 dans la partie "Acquisition du signal"

        move_screw(S, i + step)  # Le moteur travail en mode absolu par défaut G90

        print(f"Tension photodiode 1 (Volt) : {voltages_photodiode_1}")
        print(f"Taille de la liste Tension photodiode 1 : {len(voltages_photodiode_1)}")
        print(f"Tension photodiode 2 (Volt) : {voltages_photodiode_2}")
        print(f"Taille de la liste photodiode 2 : {len(voltages_photodiode_2)}")
        print(f"Pas de vis (mm) : {i}")
        print(f"Longueur d'onde (nm) : {wavelength}")
        print(f"Taille de la liste Longueur d'onde (nm) : {len(wavelength)}")

        time.sleep(time_per_step)  # Comme $110 =4mm/min et le pas de vis est de 0.5mm => Le moteur réalise un pas de vis en 7.49s
        i += step

        
        

    """
    Fin de l'acquisition
    """

    """
    Dé
    """
    if choice == '(cuve 1)':
        reference_solution=voltages_photodiode_1
        sample_solution=voltages_photodiode_2
    else:
        reference_solution=voltages_photodiode_2
        sample_solution=voltages_photodiode_1



   
    wavelength.reverse()
    reference_solution.reverse()
    sample_solution.reverse()
    no_screw.reverse()

    return  wavelength, reference_solution, sample_solution, no_screw




"""
PARTIE ACQUISITION DES DONNEES
""" 
def ACQUISITION(course_vis, nombre_de_mesure, screw_translation_speed, PULSE_FREQUENCY, DUTY_CYCLE, fichier_blanc, fichier_echantillon, Nom_echantillon, Titre, REPERTORY): # Départ 7.25mm / 21 - 7.25 = 13.75mm où 21 course de la vis total de la vis => course_vis=13.75mm
    nom_colonne_tension_blanc='Tension blanc (Volt)'

    nom_colonne_tension_echantillon='Tension échantillon (Volt)'

   
  


    [wavelength, Tension_blanc, Tension_echantillon, no_screw] = mode_precision(course_vis, nombre_de_mesure, screw_translation_speed, PULSE_FREQUENCY, DUTY_CYCLE)
    

   

    

    
    save_data_csv(fichier_echantillon, wavelength, Tension_echantillon, no_screw, 'Longueur d\'onde (nm)', nom_colonne_tension_echantillon,'Liste_pas_vis')
    save_data_csv(fichier_blanc, wavelength, Tension_blanc, no_screw, 'Longueur d\'onde (nm)', nom_colonne_tension_blanc,'Liste_pas_vis')

    a=str(state_screw_motor(S))
    while 'Idle' not in a: # 'Idle': Instruction GRBL pour dire que ce moteur est à l'arrêt / 'Run' le moteur tourne
        a=str(state_screw_motor(S))

    print(a)
    
    grbl_parameter_screw_motor(S)
    return_screw(S,course_vis, screw_translation_speed=10)
    grbl_parameter_screw_motor(S)    

    graph(fichier_blanc, fichier_echantillon, Nom_echantillon, Titre, REPERTORY)




"""
LANCEMENT DU PROGRAMME
"""

# Concaténer les variables pour former le chemin d'accès complet




course_vis=2 # 7mm
nombre_de_mesures=10 # A modifier si on veut être plus précis
screw_translation_speed=10 # mm/min

Nom_echantillon=input("Nom de l'échantillon :") # A modifier si on change de composé chimique


fichier_blanc=  REPERTORY + '\Tension_blanc_' + DATE + "_" + SLOT_SIZE + '.csv'
fichier_echantillon=  REPERTORY + '\Tension_echantillon_' + DATE + "_" + SLOT_SIZE + '.csv'


Titre="Absorbance_"+ "_" + Nom_echantillon+ DATE+"_"+ SLOT_SIZE  

ACQUISITION(course_vis, nombre_de_mesures, screw_translation_speed, PULSE_FREQUENCY, DUTY_CYCLE, fichier_blanc, fichier_echantillon, Nom_echantillon, Titre, REPERTORY) # course_vis 13.75 mm / 260 points / screw_translation_speed = 4mm/min
#graph(fichier_blanc, fichier_echantillon, Nom_echantillon, Titre, REPERTORY)

#mode_precision(course_vis, nombre_de_mesures, screw_translation_speed, Frequence_creneau=np.array([Frequence_creneau]), DUTY_CYCLE=np.array([DUTY_CYCLE]))

