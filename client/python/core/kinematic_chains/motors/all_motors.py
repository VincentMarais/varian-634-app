"""
Ce programme pilote tout les moteurs présent sur le VARIAN 634
"""

def state_motors(arduino_motors):
    """
    But: Connaître l'état de tout les moteurs du VARIAN 634 si l'un moteur 
    des est en mouvement "Run" ou non "Idle"

    Entrée : arduino_motors     

    Sortie : renvoie les 10 premiers caractère de l'état du moteur 

    """
    g_code='?' + '\n'
    arduino_motors.write(g_code.encode())
    return arduino_motors.read(40) # 10: On lit 10 caractère dans le serial

def grbl_parameter_motors(arduino_motors):
    """
    Entree : arduino_motors

    Sortie : Aucune

    But: Afficher de type de déplacement du moteur : G90 déplacement absolue
    """
    g_code='$G' + '\n'
    arduino_motors.write(g_code.encode())
    print(arduino_motors.read(75)) # 75 because the information on G90 is at this position

def stop_motors(arduino_motors):
    """
    Fonction qui force l'arrêt des moteurs 
    """
    g_code = '!'+'\n'
    arduino_motors.write(g_code.encode())

def wait_for_motor_idle(arduino_motors):
    """
    Attend que le moteur soit au repos.
    """
    gcode_state_motor = str(state_motors(arduino_motors))
    while 'Idle' not in gcode_state_motor:
        gcode_state_motor = str(state_motors(arduino_motors))
    print(gcode_state_motor)
# End-of-file (EOF)
