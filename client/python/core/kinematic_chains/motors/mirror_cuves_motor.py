"""
The pilot program controls the mirror-linked engine, allowing the 
transition from the sample chamber to the reference chamber.

"""
import time
from pyfirmata import util, INPUT
from all_motors import stop_motors

def move_mirror_cuves_motor(arduino_motors, plastic_disc_position):
    """
        # Fonction qui fait tourner le miroir tournant aux niveaux des cuves du VARIAN 634
        # Entry : 
            - arduino_motors : variable d'initialisation de l'arduino 
            lié au moteur qui pilote le miroir
            
            - plastic_disc_position : position relative du disque de plastique lié au moteur
    
        """
    g_code= '$X'+'\n' # $ Unlock la sécurité
    #Le moteur ce déplace linéairement de -pas_vis (retour_moteur_vis en arrière)
    arduino_motors.write(g_code.encode())
    g_code = 'G91\n' + 'G0Y' + str(plastic_disc_position) + '\n'
    arduino_motors.write(g_code.encode())

def optical_fork_state(arduino_optical_fork):#   Initialiser la communication série avec l'Arduino
    """
    Entrée: arduino_optical_fork = serial.Serial('COM6', 9600)  
    # Remplacez 'COM3' par le port série correspondant à votre Arduino    
    Grâce au code optical_fork.ino que l'on doit lancer sur la carte arduino
    """
    while True:
        # Lire les données envoyées par l'Arduino
        data = arduino_optical_fork.readline().decode('utf-8').strip()
        if data == "up":  # Si la fourche optique est dans l'état 1
            return True
        elif data == "low":
            return False

        else:
            print("Le pin n\'est pas reconnu.")



def initialisation_mirror_cuves_motor(arduino_optical_fork, arduino_motors):
    """
    Fonction pour déterminer la position de mon moteur 
    """
    # Configurer le port digital 3 en tant qu'entrée
    arduino_optical_fork.digital[3].mode = INPUT  # Modifié ici

# Créer une instance d'Itérateur pour ne pas manquer les données entrantes
    it = util.Iterator(arduino_optical_fork)
    it.start()

# Permettre à l'itérateur de démarrer
    time.sleep(1)
    digital_value = arduino_optical_fork.digital[3].read()
    while digital_value is True:
        # Lire la valeur du port digital 3
        digital_value = arduino_optical_fork.digital[3].read()
        print(digital_value)
        move_mirror_cuves_motor(arduino_motors, plastic_disc_position=0.4)
        digital_value = arduino_optical_fork.digital[3].read()
        print(digital_value)
    stop_motors(arduino_motors)
# End-of-file (EOF)
