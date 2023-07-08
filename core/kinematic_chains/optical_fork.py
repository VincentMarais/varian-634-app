def fourche_optique_etat(pin):
        # définir le pin 3 comme entrée


    # une boucle pour lire l'état du pin
    state = pin.read()  # lire l'état du pin
            
    if state is not None:
            if state:
                        return 'Bonne photodiode'
            else:
                        return 'Mauvaise photodiode'
    else:
        return 'Le pin n\'est pas reconnu.'
    

