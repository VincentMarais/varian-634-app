"""
This program will control the motors that manage 
the variable slits system of the VARIAN 634
"""

import time
from pyfirmata import util, INPUT

# CARACTERISTIQUE GRBL MOTEUR

def initialisation_slits_motor(arduino_motors):
    """
    Initialise le système de fentes variables pour le début de l'expérience.

    Args:
        arduino_motors (serial.Serial): Instance représentant le moteur Arduino connecté aux fentes variables.
    Returns:
        Aucune
    """
    g_code = 'G90' + '\n'  # Le moteur se déplace en mode absolu
    arduino_motors.write(g_code.encode())
    time.sleep(0.5)

def move_slits(arduino_motors):
    """
    Déplace le système de fentes variables.

    Args:
        arduino_motors (serial.Serial): Instance représentant le moteur Arduino connecté aux fentes variables.
    Returns:
        Aucune
    """
    slit_course = 0.2
    g_code = 'G90\n' + 'G0Z' + str(slit_course) + '\n'  # Le moteur se déplace en mode absolu
    arduino_motors.write(g_code.encode())

def return_slit(arduino_motors):
    """
    Déplacement arrière du système de fentes variables.

    Args:
        arduino_motors (serial.Serial): Instance représentant le moteur Arduino connecté aux fentes variables.
    Returns:
        Aucune
    """
    slit_course = 0.2
    g_code = 'G91' + 'G0Z-' + str(slit_course) + '\n'  # Le moteur se déplace en mode relatif
    arduino_motors.write(g_code.encode())

def end_stop_state_slits(arduino_end_stop, arduino_motors):
    """
    Donne l'état des capteurs de fin de course au niveau du système de fentes variables.

    Args:
        arduino_end_stop (serial.Serial): Instance représentant les capteurs de fin de course connectés à Arduino.
        arduino_motors (serial.Serial): Instance représentant le moteur Arduino connecté aux fentes variables.
    Returns:
        Aucune
    """
    arduino_end_stop.digital[4].mode = INPUT  # Configurer le capteur de fin de course en mode entrée

    # Créer une instance d'itérateur pour surveiller les données entrantes
    it = util.Iterator(arduino_end_stop)
    it.start()

    # Permettre à l'itérateur de démarrer
    time.sleep(1)
    digital_value = arduino_end_stop.digital[4].read()

    while digital_value is False:
        # Lire la valeur du port digital 4 (capteur de fin de course)
        digital_value = arduino_end_stop.digital[4].read()
        print(digital_value)
        move_slits(arduino_motors)
        digital_value = arduino_end_stop.digital[4].read()
        print(digital_value)

    # Envoyer un signal d'arrêt lorsque le capteur de fin de course est activé
    g_code = '!' + '\n'
    arduino_motors.write(g_code.encode())

def slit_use(arduino_motors):
    """
    Donne la position du moteur qui pilote le système de fentes variables afin de savoir quelle fente est utilisée.

    Args:
        arduino_motors (serial.Serial): Instance représentant le moteur Arduino connecté aux fentes variables.
    
    Returns:
        position_z (str): Position actuelle du moteur selon l'axe Z.
    """
    # Demande la position actuelle du moteur selon l'axe Z
    arduino_motors.write(b"?z\n")
    reponse = arduino_motors.readline().decode().strip()
    position_z = reponse.split(":")[1]
    return position_z
# End-of-file (EOF)



import serial  
from pyfirmata import Arduino, util, INPUT

# INITIALISATION MOTEUR:

COM_PORT_MOTORS = 'COM3'
COM_PORT_SENSORS = 'COM9'
BAUD_RATE = 115200
INITIALIZATION_TIME = 2

arduino_motors = serial.Serial(COM_PORT_MOTORS, BAUD_RATE)
arduino_motors.write("\r\n\r\n".encode()) # encode pour convertir "\r\n\r\n" 
time.sleep(INITIALIZATION_TIME)   # Attend initialisation un GRBL
arduino_motors.flushInput()  # Vider le tampon d'entrée, en supprimant tout son contenu.

# INITIALISATION Forche optique:

arduino_optical_fork = Arduino(COM_PORT_SENSORS)
g_code='$X' + '\n'
arduino_motors.write(g_code.encode())
# Test move_mirror_cuves_motor
move_slits(arduino_motors=arduino_motors)