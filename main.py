import serial  
import time 

# Méthode VARIAN 634
from core.dual_beam import ACQUISITION

# Data processing
from core.utils.Creation_repertoire import creation_repertoire_date_slot 


"""
Initialisation fichier pour le programme 
"""
[REPERTORY, DATE, SLOT_SIZE] = creation_repertoire_date_slot()


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

ACQUISITION(S, screw_travel, number_measurements, screw_translation_speed, reference_solution_file, sample_solution_file, sample_name, title, REPERTORY) # screw_travel 13.75 mm / 260 points / screw_translation_speed = 4mm/min


