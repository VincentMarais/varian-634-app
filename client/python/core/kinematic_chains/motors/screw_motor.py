"""
This program controls the motor that drives the screw which allows the 
rotation of the reflection diffraction grating of the VARIAN 634.
"""

import time
from typing import Any
from pyfirmata import util, INPUT

# CARACTERISTIQUE GRBL MOTEUR

def state_motors(arduino_motors):
    """
    But: Connaître l'état de tout les moteurs du VARIAN 634 si l'un moteur 
    des est en mouvement "Run" ou non "Idle"

    Entrée : arduino_motors     

    Sortie : renvoie les 10 premiers caractère de l'état du moteur 

    """
    g_code='?' + '\n'
    arduino_motors.write(g_code.encode())
    return arduino_motors.read(40) # 10: On lit 10 caractère dans le serial

def grbl_parameter_motors(arduino_motors):
    """
    Entree : arduino_motors

    Sortie : Aucune

    But: Afficher de type de déplacement du moteur : G90 déplacement absolue
    """
    g_code='$G' + '\n'
    arduino_motors.write(g_code.encode())
    print(arduino_motors.read(75)) # 75 because the information on G90 is at this position

def stop_motors(arduino_motors):
    g_code = '!'+'\n'
    arduino_motors.write(g_code.encode())
# initialization of the motor

def modify_screw_translation_speed(arduino_motors, screw_translation_speed):
    """
    Modifie la vitesse de translation de la vis
    """
    g_code = '$110=' + str(screw_translation_speed) + '\n'
    arduino_motors.write(g_code.encode())
    time.sleep(0.5)


def initialisation_motor_screw(arduino_motors, screw_translation_speed):
    """
    Initialise la vis qui déplace le réseau de diffraction pour le début de l'expérience
    """
    g_code= 'G90'+ '\n' # Le moteur se déplace en relatif
    arduino_motors.write(g_code.encode())
    time.sleep(0.5)
    modify_screw_translation_speed(arduino_motors, screw_translation_speed)

# screw cinematics

def move_screw(arduino_motors, screw_course, screw_translation_speed):
    """
    Déplace la vis qui déplace le réseau de diffraction
    """
    modify_screw_translation_speed(arduino_motors, screw_translation_speed)
    g_code= 'G90\n' + 'G0X' + str(screw_course) + '\n' # Le moteur ce déplace en relatif
    arduino_motors.write(g_code.encode())

def return_screw(arduino_motors, screw_course, screw_translation_speed):
    """
    Déplacement arrière de la vis
    """
    modify_screw_translation_speed(arduino_motors, screw_translation_speed)
    g_code= 'G91'+ 'G0X-' + str(screw_course) + '\n' # Le moteur ce déplace en relatif
    #Le moteur ce déplace linéairement de -pas_vis (retour_moteur_vis en arrière)
    arduino_motors.write(g_code.encode())


def end_stop_state(arduino_end_stop, arduino_motors,screw_course, screw_translation_speed):
    """
    Donne l'état des capteurs de fin de course on niveau de la vis 
    """
    arduino_end_stop.digital[2].mode = INPUT  # Modifié ici

# Créer une instance d'Itérateur pour ne pas manquer les données entrantes
    it = util.Iterator(arduino_end_stop)
    it.start()

# Permettre à l'itérateur de démarrer
    time.sleep(1)
    digital_value = arduino_end_stop.digital[2].read()
    while digital_value is False:
        # Lire la valeur du port digital 3
        digital_value = arduino_end_stop.digital[2].read()
        print(digital_value)
        move_screw(arduino_motors, screw_course, screw_translation_speed)
        digital_value = arduino_end_stop.digital[2].read()
        print(digital_value)

def position_vis(arduino_motors):
    """
    Donne la position de la vis 
    """
    # Demande la position actuelle du moteur selon l'axe X
    arduino_motors.write(b"?x\n")
    reponse = arduino_motors.readline().decode().strip()
    position_x = reponse.split(":")[1]
    return position_x
