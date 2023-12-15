"""
The pilot program controls the mirror-linked engine, allowing the 
transition from the sample chamber to the reference chamber.

"""
import time
from pyfirmata import util, INPUT
from kinematic_chains.motors.all_motors import stop_motors, position_xyz #kinematic_chains.motors.all_motors

def move_mirror_cuves_motor(arduino_motors, plastic_disc_position):
    """
    Fonction qui fait tourner le miroir tournant aux niveaux des cuves du VARIAN 634.
    
    Args: 
        arduino_motors (serial.Serial): Instance représentant le moteur Arduino lié au miroir.
        plastic_disc_position (float): Position relative du disque de plastique lié au moteur.
    """
    g_code = '$X' + '\n'  # Désactive la sécurité
    arduino_motors.write(g_code.encode())
    g_code = 'G91\n' + 'G0Y' + str(plastic_disc_position) + '\n'
    arduino_motors.write(g_code.encode())

def initialisation_mirror_cuves_motor(arduino_motors, arduino_optical_fork):
    """
    Fonction pour initialiser et déterminer la position du moteur du miroir.
    
    Args:
        arduino_motors (serial.Serial): Instance représentant le moteur Arduino du miroir.
        arduino_optical_fork (serial.Serial): Instance de communication avec l'Arduino de la fourche optique.
    """
    # Configuration du port digital 3 en tant qu'entrée
    arduino_optical_fork.digital[3].mode = INPUT
    
    # Création d'une instance d'itérateur pour surveiller les données entrantes
    it = util.Iterator(arduino_optical_fork)
    it.start()
    
    # Attente d'une seconde pour permettre à l'itérateur de démarrer
    time.sleep(1)
    
    digital_value = arduino_optical_fork.digital[3].read()
    
    while digital_value is True:
        digital_value = arduino_optical_fork.digital[3].read()
        print(digital_value)
        move_mirror_cuves_motor(arduino_motors, plastic_disc_position=0.4)
        digital_value = arduino_optical_fork.digital[3].read()
        print(digital_value)
    stop_motors(arduino_motors)

def initialisation_mirror_cuves_motor_v2(arduino_motors, arduino_optical_fork):
    """
    Fonction pour initialiser du moteur du miroir sur la cuve 1, basé sur 
    la position 
    
    Args:
        arduino_motors (serial.Serial): Instance représentant le moteur Arduino du miroir.
        arduino_optical_fork (serial.Serial): Instance de communication avec l'Arduino de la fourche optique.
    """
    # Configuration du port digital 3 en tant qu'entrée
    arduino_optical_fork.digital[3].mode = INPUT
    
    # Création d'une instance d'itérateur pour surveiller les données entrantes
    it = util.Iterator(arduino_optical_fork)
    it.start()
    
    # Attente d'une seconde pour permettre à l'itérateur de démarrer
    time.sleep(1)
    
    digital_value = arduino_optical_fork.digital[3].read()
    g_code = '$X' + '\n'  # Désactive la sécurité
    arduino_motors.write(g_code.encode())
    g_code = 'G90\n' + 'G0Y1' +'\n'
    arduino_motors.write(g_code.encode())
    while digital_value is True:
        digital_value = arduino_optical_fork.digital[3].read()
        print(digital_value)        
    pos_y=position_xyz(arduino_motors=arduino_motors)[1]
    g_code="G0Y" + str(pos_y) + '\n'
    arduino_motors.write(g_code.encode())
    print(pos_y)


# End-of-file (EOF)
