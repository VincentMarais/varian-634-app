import csv
import itertools

class CSVTransformer:
    def __init__(self, path):
        self.path = path
    
    def save_data_csv(self, data_list, title_list, file_name):
        """
        Program transform the python list on csv file

        """
        path_file = f"{self.path}/{file_name}.csv"
        # Transposer la liste de données
        data_transposed = list(itertools.zip_longest(*data_list))
        with open(path_file, 'w', newline='', encoding='utf-8') as file_csv:
            writer = csv.writer(file_csv)
            # Écrire les titres en tant que première ligne
            writer.writerow(title_list)
            # Écrire les données transposées
            for row in data_transposed:
                writer.writerow(row)
        return path_file


    def add_column_to_csv(self, original_file, new_column_names, new_column_data):
        # Open the original CSV file in read mode
        original_file=f"{self.path}/{original_file}.csv"
        # Open the CSV file in read mode
        with open(original_file, 'r') as input_file:
            # Create a CSV reader
            csv_reader = csv.reader(input_file)
            
            # Read existing data
            lines = list(csv_reader)
            header = lines[0]

        for k in range(len(new_column_names)):
            header.append(new_column_names[k])

        # Add a new column with the specified data as much as possible
        for i in range(1, len(lines)):            
            for j in range(len(new_column_names)):
                if j < len(new_column_data) and i - 1 < len(new_column_data[j]):
                    lines[i].append(new_column_data[j][i - 1])
                else:
                    lines[i].append('')  # Add an empty string if data is insufficient
        # Open the CSV file in write mode
        with open(original_file, 'w', newline='', encoding="utf-8") as output_file:
            # Create a CSV writer
            csv_writer = csv.writer(output_file)
            
            # Write the modified lines to the original CSV file
            csv_writer.writerows(lines)




if __name__ == "__main__":
    # Exemple d'utilisation de la classe
    path = "./experiments/experiments_2023/experiments_12_2023/experiments_15_12_2023/Fente_2nm"
    transformer = CSVTransformer(path=path)
    # Appeler la méthode pour sauvegarder les données au format CSV
    transformer.save_data_csv(data_list=[[1, 2, 3], [4, 5, 6],[1]], title_list=['Absorbance', 'Longueur d\'onde (nm)', 'C'], file_name='nom_fichier')
    # Example usage of the function
    original_file = 'nom_fichier'
    new_column_names = ['NewColumn1', 'NewColumn2', 'NewColumn3']
    new_column_data = [
        ['value1', 'value2', 'value3', 'value4', 'value5'],
        ['data1', 'data2', 'data3', 'data4', 'data5'],
        ['info1', 'info2', 'info3', 'info4', 'info5']
    ]

    transformer.add_column_to_csv(original_file, new_column_names, new_column_data)
    