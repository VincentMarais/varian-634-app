import csv


# Fonction pour écrire les données dans un fichier CSV
def sauvegarder_donnees(nom_fichier, Liste_longueurs_d_onde, Liste_tensions, Liste_pas_vis, titre_1, titre_2, titre_3): # nom_Fichier: str / Liste_longueurs_d_onde, Liste_tensions: Liste / titre_1, titre_2: str
    with open(nom_fichier, 'w', newline='') as fichier_csv:
        writer = csv.writer(fichier_csv)
        writer.writerow([titre_1, titre_2,titre_3])
        for i in range(len(Liste_longueurs_d_onde)):
            writer.writerow([Liste_longueurs_d_onde[i], Liste_tensions[i], Liste_pas_vis[i]])
