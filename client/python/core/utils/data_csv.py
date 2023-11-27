"""
Program transform the python list on csv file
"""

import csv
import itertools
import pandas as pd
from directory_creation import path_creation

def save_data_csv(path, file_name, data_list, title_list):

    """
    Program transform the python list on csv file

    """
    path_file = path + '/' + file_name + '.csv'
    # Transposer la liste de données
    data_transposed = list(itertools.zip_longest(*data_list))
    with open(path_file, 'w', newline='', encoding='utf-8') as file_csv:
        writer = csv.writer(file_csv)
        # Écrire les titres en tant que première ligne
        writer.writerow(title_list)
        # Écrire les données transposées
        for row in data_transposed:
            writer.writerow(row)





def csv_experiment(path,sample_reference_file, sample_analyzed_file):
    path_sample_reference=path+ '/'+ sample_reference_file
    path_sample_analyzed=path+ '/'+ sample_analyzed_file
    data_sample_reference = pd.read_csv(path_sample_reference,  encoding='ISO-8859-1')
    data_2= pd.read_csv(path_sample_analyzed,  encoding='ISO-8859-1')
# Obtenir les colonnes 'Longueur d\'onde' et voltage Blanc et voltage échantillon
    wavelength = data_sample_reference['Longueur d\'onde (nm)']
    voltage_sample_reference = data_sample_reference['Tension blanc (Volt)']
    voltage_sample_analyzed= data_2['Tension échantillon (Volt)']

    return wavelength, voltage_sample_reference, voltage_sample_analyzed


