"""
The pilot program controls the mirror-linked engine, allowing the 
transition from the sample chamber to the reference chamber.

"""


import time

def move_mirror_cuves_motor(arduino_motors, plastic_disc_position):
    """
        # Fonction qui fait tourner le miroir tournant aux niveaux des cuves du VARIAN 634
        # Entry : 
            - arduino_motors : variable d'initialisation de l'arduino 
            lié au moteur qui pilote le miroir
            
            - plastic_disc_position : position relative du disque de plastique lié au moteur
    
        """
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
        if data == "Fourche optique libre":  # Si la fourche optique est dans l'état 1
            return True
        elif data == "Fourche optique obstruée":
            return False

        else:
            print("Le pin n\'est pas reconnu.")

def initialisation_mirror_cuves_motor(arduino_optical_fork, arduino_motors):
    """
    Function for initializing the analysis on the reference sample.
    """
    while True:
        state_optical_fork = optical_fork_state(arduino_optical_fork)

        if state_optical_fork is True:
            print("nous sommes sur la cuve de référence")
            break

        if state_optical_fork is False:
            print("TOURNE 60° car nous ne sommes sur la cuve de référence")
            for direction in [0.4, -0.4]:
                move_mirror_cuves_motor(arduino_motors, direction)
                time.sleep(1)

        else:
            print(state_optical_fork)
# End-of-file (EOF)
