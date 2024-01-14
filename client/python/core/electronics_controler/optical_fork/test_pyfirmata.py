from pyfirmata import Arduino, util, INPUT
import time

pin=2
# Remplacer 'COM3' par le nom de port de votre Arduino
board = Arduino('COM9')

# Configurer le port digital 3 en tant qu'entrée
board.digital[pin].mode = INPUT  # Modifié ici

# Créer une instance d'Itérateur pour ne pas manquer les données entrantes
it = util.Iterator(board)
it.start()

# Permettre à l'itérateur de démarrer
time.sleep(1)

while True:
    # Lire la valeur du port digital 3
    digital_value = board.digital[pin].read()

    # Afficher la valeur
    print(f"Valeur lue sur le port digital {pin} :", digital_value)

    # Attendre un peu avant de lire à nouveau
    time.sleep(0.1)
