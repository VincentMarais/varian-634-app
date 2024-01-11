import os

def afficher_fichiers_repertoire(chemin_repertoire):
    list_files=[]
    with os.scandir(chemin_repertoire) as entries:
        for entry in entries:
            if entry.is_file():
                list_files.append(entry)
    return list_files
# Exemple d'utilisation
chemin = './client/python/core'
print(afficher_fichiers_repertoire(chemin))
