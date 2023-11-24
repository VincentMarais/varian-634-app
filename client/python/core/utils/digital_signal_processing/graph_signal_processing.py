# This program will plot all the data 
import os

def creaction_de_chemin(CHEMIN, Grandeur_physique):
    chemin = os.path.join(CHEMIN, Grandeur_physique)

    if not os.path.exists(chemin):
    # Créer le répertoire en utilisant le chemin d'accès
        os.makedirs(chemin)
        print("Répertoire créé avec succès :", chemin)
    else:
        print("Le répertoire existe déjà :", chemin)

    return chemin


