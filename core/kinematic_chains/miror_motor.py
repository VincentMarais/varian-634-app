import serial  
import time 
import re

# Constantes:


def position_moteur_x(s):
    # Demande la position actuelle du moteur selon l'axe X
    s.write(b"?x\n")
    reponse = s.readline().decode().strip()
    position_x = reponse.split(":")[1]
    return int(position_x)



def position_XYZ_vis(s):
    g_code= "?" + '\n' 
    s.write(g_code.encode())
    time.sleep(0.1)

    # Lire et traiter la réponse
    response = str(s.readline())
    print("Réponse brute :", response)
    while 'MPos' not in response:
        response = str(s.readline())
    
        # Extraire les coordonnées X, Y, et Z
    match = re.search(r"MPos:([-+]?[0-9]*\.?[0-9]+),([-+]?[0-9]*\.?[0-9]+),([-+]?[0-9]*\.?[0-9]+)", response)
        
    x_pos, y_pos, z_pos = [float(coordinate) for coordinate in match.groups()]
    
    return x_pos


"""
Les méthodes reset_input_buffer() et flushInput() sont toutes deux utilisées pour vider le tampon d'entrée (input buffer) d'un port série. 
Cependant, il y a une différence entre ces deux méthodes.
reset_input_buffer() est une méthode de la bibliothèque PySerial qui permet de vider complètement le tampon d'entrée du port série. 
Cela signifie que toutes les données en attente dans le tampon d'entrée seront supprimées. 
Cette méthode est utile lorsque vous voulez vous assurer que le tampon d'entrée est vide avant de recevoir de nouvelles données.

flushInput() est également une méthode de PySerial qui permet de vider le tampon d'entrée. Cependant, contrairement 
à reset_input_buffer(), flushInput() ne supprime pas toutes les données en attente dans le tampon d'entrée. 
Au lieu de cela, elle supprime uniquement les données qui n'ont pas encore été lues par l'application. 
Cela peut être utile si vous voulez vider le tampon d'entrée sans perdre les données qui ont déjà été lues.

En résumé, la principale différence entre reset_input_buffer() et flushInput() est que la première supprime toutes les 
données en attente dans le tampon d'entrée, tandis que la seconde supprime uniquement les données qui n'ont pas encore 
été lues par l'application. Il est important de choisir la méthode appropriée en fonction de vos besoins en matière de 
gestion des données série.

"""

"""
Caractérisation DU MOTEUR

"""

def etat_mot(s):
    """
    Entree : Aucune

    Sortie : renvoie les 10 premiers caractère de l'état du moteur 

    But: Savoir si le moteur est en mouvement "Run" ou non "Idle"
    """
    g_code='?' + '\n'
    s.write(g_code.encode())
    return s.read(40) # 10: On lit 10 caractère dans le serial

def param_mot(s):    
    """
    Entree : Aucune

    Sortie : Aucune

    But: Afficher de type de déplacement du moteur : G90 déplacement absolue
    """
    g_code='$G' + '\n'
    s.write(g_code.encode())
    print(s.read(75))



def position_moteur_x(s):
    # Demande la position actuelle du moteur selon l'axe X
    g_code= "?" + '\n' 
    s.write(g_code.encode())
    time.sleep(0.1)
    reponse = str(s.readline())
    while 'MPos' not in reponse:
        reponse = str(s.readline())
        print(reponse)
    
    #reponse = reponse.split(":")
    #position_x=reponse.split(",")[0]
    #return float(position_x)

def modif_vitesse_translation(s, vitesse_translation_vis):
    g_code = '$110=' + str(vitesse_translation_vis) + '\n'
    s.write(g_code.encode())
    time.sleep(0.5)


def deplacement_domaine_visible(s):
        g_code= 'G90'+ '\n'
        s.write(g_code.encode())
        time.sleep(0.5)
        gcode_1= 'G0X7.25' + '\n'
        s.write(gcode_1.encode())

        
def deplacer_moteur_vis(s,course_vis, vitesse_translation_vis): # Fonction qui pilote le moteur      
        g_code= 'G90'+ '\n'
        s.write(g_code.encode())
        time.sleep(0.5)
        modif_vitesse_translation(vitesse_translation_vis)        
        gcode_1= 'G0X' + str(course_vis) + '\n'
        s.write(gcode_1.encode())


def deplacer_vis(s,pas): # Fonction qui pilote le moteur      
        g_code= 'G90'+ '\n' # Le moteur ce déplace en relatif
        s.write(g_code.encode())
        time.sleep(0.5)
        gcode_1= 'G0X' + str(pas) + '\n'
        s.write(gcode_1.encode())


def deplacer_moteur_miroir(s,course_vis): # Fonction qui pilote le moteur      
        g_code= 'G91'+ '\n'
        s.write(g_code.encode())
        time.sleep(0.5)
        gcode_1= 'G0Y' + str(course_vis) + '\n'
        s.write(gcode_1.encode())

        

def retour_moteur_vis(s, course_vis, vitesse_translation_vis): 
        modif_vitesse_translation(s,vitesse_translation_vis)
        g_code= 'G91'+ '\n' # Le moteur ce déplace en relatif
        s.write(g_code.encode())
        time.sleep(0.5)
        gcode_1= 'G0X-' + str(course_vis) + '\n' # Le moteur ce déplace linéairement de -pas_vis (retour_moteur_vis en arrière)
        s.write(gcode_1.encode())


def deplacement_double_moteur(s,course_vis, course_miroir, vitesse_translation_vis):
     deplacer_moteur_vis(s,course_vis, vitesse_translation_vis)
     deplacer_moteur_miroir(s,course_miroir)

def test_double_faisceau(s,course_vis,pas , course_miroir, vitesse_translation_vis):
    i=0
    while i < course_vis:
        i+=pas
        deplacer_moteur_vis(s,i, vitesse_translation_vis)
        deplacer_moteur_miroir(s,course_miroir)
        #deplacer_moteur_miroir(-course_miroir)

        
    retour_moteur_vis(s,course_vis, vitesse_translation_vis)

"""
deplacer_moteur(-0.754,4)
s=str(etat_mot())
while 'Idle' not in s:
    s=str(etat_mot())
"""


def acquisition(s,n,vitesse_translation_vis):
    i=0
    g_code = '$110=' + str(vitesse_translation_vis) + '\n'
    s.write(g_code.encode())
    while i<n:
        gcode_1= 'G0X' + str(i) + '\n' # Le moteur ce déplace linéairement de -pas_vis (retour_moteur_vis en arrière)
        s.write(gcode_1.encode())
        time.sleep(2)
        i=0.05+i
    retour_moteur_vis(s,n,10)



