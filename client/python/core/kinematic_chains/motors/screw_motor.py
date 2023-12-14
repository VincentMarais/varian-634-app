"""
This program controls the motor that drives the screw which allows the 
rotation of the reflection diffraction grating of the VARIAN 634.
"""

import time
from pyfirmata import util, INPUT

def modify_screw_translation_speed(arduino_motors, screw_translation_speed):
    """
    But : Modifie la vitesse de translation de la vis
    Entree : 
        arduino_motors (serial.Serial): Characterization of the motor Arduino connected to the screw
        screw_translation_speed (int) : Change la vitesse de translation de la vis
    
    Sortie : Aucune
    """
    g_code = '$110=' + str(screw_translation_speed) + '\n'
    arduino_motors.write(g_code.encode())
    time.sleep(0.5)


# screw cinematics

def move_screw(arduino_motors, screw_course, screw_translation_speed):
    """
    Déplace la vis qui déplace le réseau de diffraction
    
    Args:
        arduino_motors (serial.Serial): Instance représentant le moteur Arduino connecté à la vis.
        screw_course (float): Position de la vis à laquelle se déplacer.
        screw_translation_speed (int): Vitesse de translation de la vis à régler.
    
    Returns:
        Aucune
    """
    modify_screw_translation_speed(arduino_motors, screw_translation_speed)
    g_code = 'G90\n' + 'G0X' + str(screw_course) + '\n'  # Le moteur se déplace en mode absolu
    arduino_motors.write(g_code.encode())

def reset_screw_position(arduino_motors, screw_course, screw_translation_speed):
    """
    Déplacement arrière de la vis
    
    Args:
        arduino_motors (serial.Serial): Instance représentant le moteur Arduino connecté à la vis.
        screw_course (float): Position de la vis à laquelle revenir en arrière.
        screw_translation_speed (int): Vitesse de translation de la vis à régler.
    
    Returns:
        Aucune
    """
    modify_screw_translation_speed(arduino_motors, screw_translation_speed)
    g_code = 'G91' + 'G0X-' + str(screw_course) + '\n'  # Le moteur se déplace en mode relatif
    arduino_motors.write(g_code.encode())

def end_stop_state(arduino_end_stop):
    """
    Donne l'état des capteurs de fin de course au niveau de la vis
    
    Args:
        arduino_end_stop (Arduino): Instance représentant le capteur de fin de course.
            
    Returns:
        Aucune
    """
    arduino_end_stop.digital[2].mode = INPUT  # Modifie ici

    # Crée une instance d'itérateur pour ne pas manquer les données entrantes
    it = util.Iterator(arduino_end_stop)
    it.start()

    # Permet à l'itérateur de démarrer
    time.sleep(1)
    digital_value = arduino_end_stop.digital[2].read()
    return digital_value



def position_vis(arduino_motors):
    """
    Donne la position de la vis
    
    Args:
        arduino_motors (serial.Serial): Instance représentant le moteur Arduino connecté à la vis.
    
    Returns:
        position_x (str): Position actuelle de la vis sur l'axe X.
    """
    # Demande la position actuelle du moteur selon l'axe X
    arduino_motors.write(b"?x\n")
    reponse = arduino_motors.readline().decode().strip()
    position_x = reponse.split(":")[1]
    return position_x

def initialisation_motor_screw(arduino_motors, arduino_end_stop, screw_translation_speed):
    """
    Initialise la vis qui déplace le réseau de diffraction pour le début de l'expérience
    
    Args:
        arduino_motors (serial.Serial): Instance représentant le moteur Arduino connecté à la vis.
        arduino_end_stop (Arduino): Instance représentant le capteur de fin de course.
        screw_translation_speed (int): Vitesse de translation de la vis à régler.
    
    Returns:
        Aucune
    """
    g_code = 'G90' + '\n'  # Le moteur se déplace en mode absolu
    arduino_motors.write(g_code.encode())
    time.sleep(0.5)
    while end_stop_state(arduino_end_stop=arduino_end_stop) is True:
        move_screw(arduino_motors=arduino_motors, screw_course=-1, screw_translation_speed=10)
        a=end_stop_state(arduino_end_stop=arduino_end_stop)
        print(a)
    print("On est bien au départ !")
    # Replacer le moteur
    g_code = '$X' + '\n'  # Le moteur se déplace en mode absolu
    arduino_motors.write(g_code.encode())
    move_screw(arduino_motors=arduino_motors, screw_course=1,screw_translation_speed=10)
    modify_screw_translation_speed(arduino_motors=arduino_motors, screw_translation_speed=screw_translation_speed)
    print("Moteur prêt pour l'acquisition !")
    # End-of-file (EOF)
