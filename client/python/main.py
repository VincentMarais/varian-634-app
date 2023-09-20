import serial  
import time 
from pyfirmata import Arduino, util
import numpy as np
import sys
sys.path.append("C:/Users/admin/Documents/Projet_GP/Programmation_Spectro/varian-634-app/client/python")

# Méthode VARIAN 634
from core.dual_beam import acquition

# Data processing
from core.utils.directory_creation import creation_directory_date_slot 


"""
Initialisation fichier pour le programme 
"""

[REPERTORY, DATE, SLOT_SIZE] = creation_directory_date_slot()

"""
INITIALISATION DE L'ARDUINO + CARTE NI-PCI 6221
"""

# Initialisation carte NI-PCI 6221
PULSE_FREQUENCY = np.array([20.0]) # 20Hz l'amplitude de la tension est maximale aux bornes de la photodiode, si on augmente la fréquence aux bornes de la photodiode => diminution de la tension
DUTY_CYCLE = np.array([0.5]) # Déterminer un rapport cyclique optimal pour la mesure
SAMPLES_PER_CHANNEL = 30000 # Nombre d'échantillon récupéré
SAMPLE_RATE = 250000 # Fréquence d'échantillonage maximale de la carte (on récupère une partie du signal cf critère de Shannon)
CHANNELS = ['Dev1/ai0', 'Dev1/ai1']  



# INITIALISATION ARDUINO Fourche OPTIQUE
BOARD_OPTICAL_FORK = Arduino('COM8')
it = util.Iterator(BOARD_OPTICAL_FORK)
it.start()
PIN = BOARD_OPTICAL_FORK.get_pin('d:3:i')  # d pour digital, 3 pour le pin 3, i pour input


# INITIALISATION ARDUINO MOTEURS
COM_PORT = 'COM3'
BAUD_RATE = 115200
INITIALIZATION_TIME = 2
S = serial.Serial(COM_PORT, BAUD_RATE)
S.write("\r\n\r\n".encode()) # encode pour convertir "\r\n\r\n" 
time.sleep(INITIALIZATION_TIME)   # Attend initialisation un GRBL
S.flushInput()  # Vider le tampon d'entrée, en supprimant tout son contenu.


"""
LANCEMENT DU PROGRAMME
"""

screw_travel=2 # 7mm
number_measurements=10 # A modifier si on veut être plus précis
screw_translation_speed=10 # mm/min

sample_name=input("Nom de l'échantillon :") # A modifier si on change de composé chimique


reference_solution_file=  REPERTORY + '\Tension_blanc_' + DATE + "_" + SLOT_SIZE + '.csv'
sample_solution_file=  REPERTORY + '\Tension_echantillon_' + DATE + "_" + SLOT_SIZE + '.csv'


title="Absorbance_"+ "_" + sample_name + DATE+ "_" + SLOT_SIZE  



acquition(S, screw_travel, number_measurements, screw_translation_speed, reference_solution_file, sample_solution_file, sample_name, title, REPERTORY) # screw_travel 13.75 mm / 260 points / screw_translation_speed = 4mm/min

