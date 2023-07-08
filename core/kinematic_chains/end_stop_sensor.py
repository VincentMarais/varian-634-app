from pyfirmata import Arduino, util
import time
# remplacer 'COM3' par le port série correct de votre Arduino
board = Arduino('COM8')

        # utiliser l'itérateur seulement pour les entrées analogiques (non nécessaire ici)
it = util.Iterator(board)
it.start()
pin_capteur_fin_course = board.get_pin('d:2:i')  # d pour digital, 2 pour le pin 2, i pour input

def capteur_de_fin_de_course():
        # définir le pin 3 comme entrée


    # une boucle pour lire l'état du pin
    state = pin_capteur_fin_course.read()  # lire l'état du pin
            
    if state is not None:
            if state:
                        return 'Capteur déclenché'
            else:
                        return 'Capteur enclenché'
    else:
        return 'Le pin n\'est pas reconnu.'
    

