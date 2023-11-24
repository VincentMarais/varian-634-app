"""
Program pilote le moteur lié miroir celui permet de passer de la cuve avec l'échantillon, à la cuve de référence à une autre 
"""


import time 

def move_mirror_cuves_motor(s,plastic_disc_position): # Fonction qui pilote le moteur
        # Entry : 
        # s : variable d'initialisation de l'arduino lié au moteur qui pilote le miroir
        # plastic_disc_position : position relative du disque de plastique lié au moteur
        g_code = 'G91\n' + 'G0Y' + str(plastic_disc_position) + '\n'
        s.write(g_code.encode())
      

def optical_fork_state(arduino_optical_fork):#   Initialiser la communication série avec l'Arduino
    """
    Entrée: arduino_optical_fork = serial.Serial('COM6', 9600)  # Remplacez 'COM3' par le port série correspondant à votre Arduino

    
    Grâce au code optical_fork.ino que l'on doit lancer sur la carte arduino
    """
    

    while True:
        data = arduino_optical_fork.readline().decode('utf-8').strip()  # Lire les données envoyées par l'Arduino
        if data == "Fourche optique libre":  # Si la fourche optique est dans l'état 1
            return True
        elif data == "Fourche optique obstruée":
            return False

        else: 
            print("Le pin n\'est pas reconnu.")

def initialisation_mirror_cuves_motor(S,PIN):
    while True:
        state_optical_fork = optical_fork_state(PIN)

        if state_optical_fork == 'Bonne photodiode':
            print(state_optical_fork)
            break

        if state_optical_fork == 'Mauvaise photodiode':
            print("TOURNE 60° car :", state_optical_fork)
            for direction in [0.4, -0.4]:
                move_mirror_cuves_motor(S, direction)
                time.sleep(1)

        else:
            print(state_optical_fork)


# Test python pour tester le code python vérifier il avoir téléversé le code grblUpload.ino sur la carte 
# et vérifier les caractéristique GRBL dans le Serial de l'arduino $$
import serial  
import time 
import re

# INITIALISATION MOTEUR:

COM_PORT = 'COM3'
BAUD_RATE = 115200
INITIALIZATION_TIME = 2

s = serial.Serial(COM_PORT, BAUD_RATE)
s.write("\r\n\r\n".encode()) # encode pour convertir "\r\n\r\n" 
time.sleep(INITIALIZATION_TIME)   # Attend initialisation un GRBL
s.flushInput()  # Vider le tampon d'entrée, en supprimant tout son contenu.

# INITIALISATION Forche optique:

#arduino_optical_fork = serial.Serial('COM6', 9600)



# Test move_mirror_cuves_motor
move_mirror_cuves_motor(s,plastic_disc_position=0.4)