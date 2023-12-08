"""
The pilot program controls the mirror-linked engine, allowing the 
transition from the sample chamber to the reference chamber.

"""
import time
import serial
from pyfirmata import Arduino, util, INPUT

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
    s.write(g_code.encode())
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
    g_code = '!'+'\n'
    arduino_motors.write(g_code.encode())
      


# End-of-file (EOF)

# INITIALISATION MOTEUR:
COM_PORT = 'COM3'
BAUD_RATE = 115200
INITIALIZATION_TIME = 2

s = serial.Serial(COM_PORT, BAUD_RATE)
s.write("\r\n\r\n".encode()) # encode pour convertir "\r\n\r\n" 
time.sleep(INITIALIZATION_TIME)   # Attend initialisation un GRBL
s.flushInput()  # Vider le tampon d'entrée, en supprimant tout son contenu.

# INITIALISATION Forche optique:
# https://www.youtube.com/watch?v=LwV3uGqKspc&ab_channel=EuroMakers (Réinitialiser la carte)
# Constantes ARDUINO Fourche OPTIQUE
from pyfirmata import Arduino, util, INPUT
import time

arduino_optical_fork = Arduino('COM6')



initialisation_mirror_cuves_motor(arduino_optical_fork,s)