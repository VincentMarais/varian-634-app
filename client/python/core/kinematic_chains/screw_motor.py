"""
This program pilot the motor who translate the screw and le réseau de diffraction par réflexion du VARIAN 634
"""

import time
import serial
from pyfirmata import Arduino, util, INPUT

# CARACTERISTIQUE GRBL MOTEUR

def state_screw_motor(arduino_motors):
    """
    Entree : Aucune

    Sortie : renvoie les 10 premiers caractère de l'état du moteur 

    But: Savoir si le moteur est en mouvement "Run" ou non "Idle"
    """
    g_code='?' + '\n'
    arduino_motors.write(g_code.encode())
    return arduino_motors.read(40) # 10: On lit 10 caractère dans le serial

def grbl_parameter_screw_motor(arduino_motors):    
    """
    Entree : arduino_motors

    Sortie : Aucune

    But: Afficher de type de déplacement du moteur : G90 déplacement absolue
    """
    g_code='$G' + '\n'
    arduino_motors.write(g_code.encode())
    print(arduino_motors.read(75)) # 75 because the information on G90 is at this position



# initialization of the motor

def modify_screw_translation_speed(arduino_motors, screw_translation_speed):
    g_code = '$110=' + str(screw_translation_speed) + '\n'
    arduino_motors.write(g_code.encode())
    time.sleep(0.5)


def initialisation_motor_screw(arduino_motors, screw_translation_speed):
    g_code= 'G90'+ '\n' # Le moteur se déplace en relatif
    arduino_motors.write(g_code.encode())
    time.sleep(0.5)
    modify_screw_translation_speed(arduino_motors, screw_translation_speed)

# screw cinematics 
        
def move_screw(arduino_motors, screw_course, screw_translation_speed): # Fonction qui pilote le moteur
        modify_screw_translation_speed(arduino_motors, screw_translation_speed)      
        g_code= 'G90\n' + 'G0X' + str(screw_course) + '\n' # Le moteur ce déplace en relatif
        arduino_motors.write(g_code.encode())
        

def return_screw(arduino_motors, screw_course, screw_translation_speed): 
        modify_screw_translation_speed(arduino_motors, screw_translation_speed)
        g_code= 'G91'+ 'G0X-' + str(screw_course) + '\n' # Le moteur ce déplace en relatif  
        #Le moteur ce déplace linéairement de -pas_vis (retour_moteur_vis en arrière)
        arduino_motors.write(g_code.encode())


def end_stop_state(arduino_end_stop, arduino_motors,screw_course, screw_translation_speed):
    arduino_end_stop.digital[2].mode = INPUT  # Modifié ici

# Créer une instance d'Itérateur pour ne pas manquer les données entrantes
    it = util.Iterator(arduino_end_stop)
    it.start()

# Permettre à l'itérateur de démarrer
    time.sleep(1)
    digital_value = arduino_end_stop.digital[2].read()    
    while digital_value is False:
        # Lire la valeur du port digital 3
        digital_value = arduino_end_stop.digital[2].read()
        print(digital_value)
        move_screw(arduino_motors, screw_course, screw_translation_speed)    
        digital_value = arduino_end_stop.digital[2].read()
        print(digital_value)
    g_code = '!'+'\n'
    arduino_motors.write(g_code.encode())
   


def position_moteur_x(arduino_motors):
    # Demande la position actuelle du moteur selon l'axe X
    arduino_motors.write(b"?x\n")
    reponse = arduino_motors.readline().decode().strip()
    position_x = reponse.split(":")[1]
    return position_x
# Test python (vous devez suivre la même procédure expliquer dans le code mirror_cuves_motor.py)
# https://www.youtube.com/watch?v=IJER_8nqK-Y&t=16s&ab_channel=ZenToolworks (Vidéo pour le homing et regarder)
# (Regarder https://www.youtube.com/watch?v=OpaUwWouyE0&ab_channel=MichaelKlements)


# INITIALISATION MOTEUR:

COM_PORT = 'COM3'
BAUD_RATE = 115200
INITIALIZATION_TIME = 2

arduino_motors = serial.Serial(COM_PORT, BAUD_RATE)
arduino_motors.write("\r\n\r\n".encode()) # encode pour convertir "\r\n\r\n" 
time.sleep(INITIALIZATION_TIME)   # Attend initialisation un GRBL
arduino_motors.flushInput()  # Vider le tampon d'entrée, en supprimant tout son contenu.

arduino_end_stop=Arduino('COM6')
g_code='$X' + '\n'
arduino_motors.write(g_code.encode())

end_stop_state(arduino_motors=arduino_motors,arduino_end_stop=arduino_end_stop, screw_course=-1, screw_translation_speed=10)
#move_screw(arduino_motors=arduino_motors, screw_course=-1, screw_translation_speed=10)