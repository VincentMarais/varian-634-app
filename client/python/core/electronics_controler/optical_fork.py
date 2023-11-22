import time 
import serial



def optical_fork_state():#   Initialiser la communication série avec l'Arduino
    """
    
    Grâce au code optical_fork.ino que l'on doit lancer sur la carte arduino
    """
    
    arduino_optical_fork = serial.Serial('COM6', 9600)  # Remplacez 'COM3' par le port série correspondant à votre Arduino

    while True:
        data = arduino_optical_fork.readline().decode('utf-8').strip()  # Lire les données envoyées par l'Arduino
        if data == "Fourche optique libre":  # Si la fourche optique est dans l'état 1
            return True
        elif data == "Fourche optique obstruée":
            return False

        else: 
              print("Le pin n\'est pas reconnu.")

