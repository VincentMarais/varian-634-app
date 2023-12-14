"""
The pilot program controls the mirror-linked engine, allowing the 
transition from the sample chamber to the reference chamber.

"""
import time
from pyfirmata import util, INPUT
from all_motors import stop_motors #kinematic_chains.motors.all_motors

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

def optical_fork_state(arduino_optical_fork):
    """
    Fonction pour récupérer l'état de la fourche optique.
    
    Args:
        arduino_optical_fork (serial.Serial): Instance de communication avec l'Arduino de la fourche optique.

    Returns:
        bool: True si la fourche optique est en position haute, False si elle est en position basse.
    """
    while True:
        data = arduino_optical_fork.readline().decode('utf-8').strip()
        if data == "up":  # Si la fourche optique est en position haute
            return True
        elif data == "low":  # Si la fourche optique est en position basse
            return False
        else:
            print("Le pin n'est pas reconnu.")

def position_mirroir(arduino_motors):
    """
    Donne la position actuelle du miroir de la vis.
    
    Args:
        arduino_motors (serial.Serial): Instance représentant le moteur Arduino connecté au miroir.

    Returns:
        str: Position actuelle du miroir selon l'axe X.
    """
    arduino_motors.write(b"?y\n")
    reponse = arduino_motors.readline().decode().strip()
    position_x = reponse.split(":")[1]
    return position_x

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
    g_code = '~' + '\n'  
    arduino_motors.write(g_code.encode())

# End-of-file (EOF)
