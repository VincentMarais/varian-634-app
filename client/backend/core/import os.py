import os

# Obtention du répertoire de travail actuel
repertoire_actuel = os.getcwd()
print("Répertoire actuel:", repertoire_actuel)
path= os.path.join(repertoire_actuel, "baseline" )
print(path)
