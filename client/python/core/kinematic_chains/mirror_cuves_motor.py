import time 


def optical_fork_state(pin):
    # Entry : définir le pin 3 comme entrée


    # une boucle pour lire l'état du pin
    state = pin.read()  # lire l'état du pin
            
    if state is not None:
            if state:
                        return 'Bonne photodiode'
            else:
                        return 'Mauvaise photodiode'
    else:
        return 'Le pin n\'est pas reconnu.'
    



def move_mirror_cuves_motor(s,plastic_disc_position): # Fonction qui pilote le moteur      
        g_code= 'G91'+ '\n'
        s.write(g_code.encode())
        time.sleep(0.5)
        gcode_1= 'G0Y' + str(plastic_disc_position) + '\n'
        s.write(gcode_1.encode())



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

    