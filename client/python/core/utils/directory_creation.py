"""This program will create directory file with python."""

import os
import datetime

def detection_exitance_directory(path): # Path chemin d'accès
    """
    Look if the directory exist
    """
    path=os.path.join(path)
    if not os.path.exists(path):
        return False

def directory_year_month_day():
    """
    Create a directory with the current year_month_day    
    """
    current_date = datetime.datetime.now()
    current_year = current_date.strftime("%Y")
    current_month = current_date.strftime("%m_%Y")
    current_day = current_date.strftime("%d_%m_%Y")
    path = os.path.join(
        "./experiments",
        "experiments_" + current_year,
        "experiments_" + current_month,
        "experiments_" + current_day)    
    if  detection_exitance_directory(path) is False:
        os.makedirs(path)
        print("Le répertoire à été créé : ", path)
    else:
        print("Le répertoire existe déjà :", path)

    return path

def creation_directory_date_slot():
    """
    Creating a directory with the length of the slot used in the experiment.
    
    """
    slot_size=input("Taille de fente : Fente_2nm, Fente_1nm , Fente_0_5nm, Fente_0_2nm : ")
    date_today = datetime.date.today()
    date = date_today.strftime("%d_%m_%Y")
    path= directory_year_month_day()
    path = os.path.join(path, slot_size)

    # Vérifier si le répertoire existe déjà
    if not os.path.exists(path):
        # Créer le répertoire en utilisant le path d'accès
        os.makedirs(path)
        print("Répertoire créé avec succès :", path)
    else:
        print("Le répertoire existe déjà :", path)

    return path, date, slot_size
# End-of-file (EOF)