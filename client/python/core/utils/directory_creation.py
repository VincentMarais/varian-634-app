import os
import datetime

def detection_exitance_directory(chemin): # Path chemin d'accès
    chemin=os.path.join(chemin)
    if not os.path.exists(chemin):
        return False

def directory_year_month_day():
    current_date = datetime.datetime.now()
    current_year, current_month, current_day = current_date.strftime("%Y") , current_date.strftime("%m_%Y"), current_date.strftime("%d_%m_%Y") 
        
    chemin=os.path.join("./experiments","experiments_"+ current_year, "experiments_"+ current_month , "experiments_"+current_day)
    if  detection_exitance_directory(chemin)==False:
        os.makedirs(chemin)
        print("Le répertoire à été créé : ", chemin)
    else:
            print("Le répertoire existe déjà :", chemin)

    return chemin

def creation_directory_date_slot():
    Taille_de_fente=input("Taille de fente : Fente_2nm, Fente_1nm , Fente_0_5nm, Fente_0_2nm : ")
    date_aujourdhui = datetime.date.today()
    Date = date_aujourdhui.strftime("%d_%m_%Y")
    chemin= directory_year_month_day()
    chemin = os.path.join(chemin, Taille_de_fente)

    # Vérifier si le répertoire existe déjà
    if not os.path.exists(chemin):
        # Créer le répertoire en utilisant le chemin d'accès
        os.makedirs(chemin)
        print("Répertoire créé avec succès :", chemin)
    else:
        print("Le répertoire existe déjà :", chemin)

    return chemin, Date, Taille_de_fente

