"""
This program will control the motors that manage 
the variable slits system of the VARIAN 634
"""

import time
from typing import Any
from pyfirmata import util, INPUT

# CARACTERISTIQUE GRBL MOTEUR

def initialisation_slits_motor(arduino_motors):
    """
    Initialise le système de fentes variable pour le début de l'expérience
    """
    g_code= 'G90'+ '\n' # Le moteur se déplace en relatif
    arduino_motors.write(g_code.encode())
    time.sleep(0.5)

# screw cinematics

def move_slits(arduino_motors):
    """
    Déplace le système de fentes variable 
    """
    slit_course = 0.2
    g_code= 'G90\n' + 'G0Z' + str(slit_course) + '\n' # Le moteur ce déplace en relatif
    arduino_motors.write(g_code.encode())

def return_slit(arduino_motors):
    """
    Déplacement arrière du système de fentes variable
    """
    slit_course = 0.2
    g_code= 'G91'+ 'G0Z-' + str(slit_course) + '\n' # Le moteur ce déplace en relatif
    #Le moteur ce déplace linéairement de -pas_vis (retour_moteur_vis en arrière)
    arduino_motors.write(g_code.encode())


def end_stop_state_slits(arduino_end_stop, arduino_motors):
    """
    Donne l'état des capteurs de fin de course on niveau de le système de fentes variable 
    """
    arduino_end_stop.digital[4].mode = INPUT  # Modifié ici

# Créer une instance d'Itérateur pour ne pas manquer les données entrantes
    it = util.Iterator(arduino_end_stop)
    it.start()

# Permettre à l'itérateur de démarrer
    time.sleep(1)
    digital_value = arduino_end_stop.digital[4].read()
    while digital_value is False:
        # Lire la valeur du port digital 3
        digital_value = arduino_end_stop.digital[4].read()
        print(digital_value)
        move_slits(arduino_motors)
        digital_value = arduino_end_stop.digital[4].read()
        print(digital_value)
    g_code = '!'+'\n'
    arduino_motors.write(g_code.encode())

def slit_use(arduino_motors):
    """
    Donne la position du moteur qui pilote le système de fentes variable afin 
    que nous dire que quelle fente on travail  
    """
    # Demande la position actuelle du moteur selon l'axe X
    arduino_motors.write(b"?z\n")
    reponse = arduino_motors.readline().decode().strip()
    position_z = reponse.split(":")[1]
    return position_z
# End-of-file (EOF)
