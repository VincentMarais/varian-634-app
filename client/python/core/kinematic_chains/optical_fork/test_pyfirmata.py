from pyfirmata import Arduino, util, INPUT
import time

# Remplacer 'COM3' par le nom de port de votre Arduino
board = Arduino('COM6')

# Configurer le port digital 3 en tant qu'entrée
board.digital[2].mode = INPUT  # Modifié ici

# Créer une instance d'Itérateur pour ne pas manquer les données entrantes
it = util.Iterator(board)
it.start()

# Permettre à l'itérateur de démarrer
time.sleep(1)

while True:
    # Lire la valeur du port digital 3
    digital_value = board.digital[2].read()

    # Afficher la valeur
    print("Valeur lue sur le port digital 3 :", digital_value)

    # Attendre un peu avant de lire à nouveau
    time.sleep(0.1)
