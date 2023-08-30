import time 


"""
CARACTERISTIQUE GRBL MOTEUR
"""
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
    Entree : Aucune

    Sortie : Aucune

    But: Afficher de type de déplacement du moteur : G90 déplacement absolue
    """
    g_code='$G' + '\n'
    s.write(g_code.encode())
    print(s.read(75))





def modify_screw_translation_speed(s, vitesse_translation_vis):
    g_code = '$110=' + str(vitesse_translation_vis) + '\n'
    s.write(g_code.encode())
    time.sleep(0.5)


def initialisation_motor_screw(S,vitesse_translation_vis):
    g_code= 'G90'+ '\n' # Le moteur se déplace en relatif
    S.write(g_code.encode())
    time.sleep(0.5)

    modify_screw_translation_speed(S,vitesse_translation_vis)

"""
CINEMATICS 
"""
        
def move_screw(s,pas): # Fonction qui pilote le moteur      
        g_code= 'G90'+ '\n' # Le moteur ce déplace en relatif
        s.write(g_code.encode())
        time.sleep(0.5)
        gcode_1= 'G0X' + str(pas) + '\n'
        s.write(gcode_1.encode())


        

def return_screw(s, course_vis, vitesse_translation_vis): 
        modify_screw_translation_speed(s,vitesse_translation_vis)
        g_code= 'G91'+ '\n' # Le moteur ce déplace en relatif
        s.write(g_code.encode())
        time.sleep(0.5)
        gcode_1= 'G0X-' + str(course_vis) + '\n' # Le moteur ce déplace linéairement de -pas_vis (retour_moteur_vis en arrière)
        s.write(gcode_1.encode())





