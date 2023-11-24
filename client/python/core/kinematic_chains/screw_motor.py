"""
This program pilot the motor who translate the screw and le réseau de diffraction par réflexion du VARIAN 634
"""

import time 



# CARACTERISTIQUE GRBL MOTEUR

def state_screw_motor(s):
    """
    Entree : Aucune

    Sortie : renvoie les 10 premiers caractère de l'état du moteur 

    But: Savoir si le moteur est en mouvement "Run" ou non "Idle"
    """
    g_code='?' + '\n'
    s.write(g_code.encode())
    return s.read(40) # 10: On lit 10 caractère dans le serial

def grbl_parameter_screw_motor(s):    
    """
    Entree : s

    Sortie : Aucune

    But: Afficher de type de déplacement du moteur : G90 déplacement absolue
    """
    g_code='$G' + '\n'
    s.write(g_code.encode())
    print(s.read(75)) # 75 because the information on G90 is at this position



# initialization of the motor

def modify_screw_translation_speed(s, screw_translation_speed):
    g_code = '$110=' + str(screw_translation_speed) + '\n'
    s.write(g_code.encode())
    time.sleep(0.5)


def initialisation_motor_screw(S,screw_translation_speed):
    g_code= 'G90'+ '\n' # Le moteur se déplace en relatif
    S.write(g_code.encode())
    time.sleep(0.5)
    modify_screw_translation_speed(S,screw_translation_speed)

# screw cinematics 
        
def move_screw(s,screw_course, screw_translation_speed): # Fonction qui pilote le moteur
        modify_screw_translation_speed(s,screw_translation_speed)      
        g_code= 'G90\n' + 'G0X' + str(screw_course) + '\n' # Le moteur ce déplace en relatif
        s.write(g_code.encode())
        

def return_screw(s, screw_course, screw_translation_speed): 
        modify_screw_translation_speed(s,screw_translation_speed)
        g_code= 'G91'+ 'G0X-' + str(screw_course) + '\n' # Le moteur ce déplace en relatif  
        #Le moteur ce déplace linéairement de -pas_vis (retour_moteur_vis en arrière)
        s.write(g_code.encode())



# Test python (vous devez suivre la même procédure expliquer dans le code mirror_cuves_motor.py)

import serial  
import time 

# INITIALISATION MOTEUR:
    
COM_PORT = 'COM3'
BAUD_RATE = 115200
INITIALIZATION_TIME = 2

s = serial.Serial(COM_PORT, BAUD_RATE)
s.write("\r\n\r\n".encode()) # encode pour convertir "\r\n\r\n" 
time.sleep(INITIALIZATION_TIME)   # Attend initialisation un GRBL
s.flushInput()  # Vider le tampon d'entrée, en supprimant tout son contenu.

#print(state_screw_motor(s))

#grbl_parameter_screw_motor(s)

move_screw(s, screw_course=1,screw_translation_speed=10)

#return_screw(s, screw_course=1, screw_translation_speed=10)