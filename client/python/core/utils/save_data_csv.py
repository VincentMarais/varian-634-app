"""
Program transform the python list on csv file
"""

import csv
import itertools

def save_data_csv(path, file_name, data_list, title_list):

    """
    Program transform the python list on csv file

    """
    path_file = path + '/' + file_name
    # Transposer la liste de données
    data_transposed = list(itertools.zip_longest(*data_list))
    with open(path_file, 'w', newline='', encoding='utf-8') as file_csv:
        writer = csv.writer(file_csv)
        # Écrire les titres en tant que première ligne
        writer.writerow(title_list)
        # Écrire les données transposées
        for row in data_transposed:
            writer.writerow(row)
