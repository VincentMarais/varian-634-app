"""
Program manage CSV data of VARIAN 634 in acquisition
"""

import csv
import itertools

class CSVTransformer:
    """
    A class to manage CSV data of VARIAN 634 in acquisition.
    
    ...

    Attributes
    ----------
    path : str
        The path where the CSV files are located.

    Methods
    -------
    save_data_csv(data_list, title_list, file_name):
        Saves the provided data to a CSV file.

    add_column_to_csv(original_file, new_column_names, new_column_data):
        Adds new columns to an existing CSV file.
    """
    
    def __init__(self, path):
        """
        Constructs all the necessary attributes for the CSVTransformer object.

        Parameters
        ----------
        path : str
            The path where the CSV files are located.
        """
        self.path = path
    
    def save_data_csv(self, data_list, title_list, file_name):
        """
        Transforms and saves the provided data to a CSV file.

        Parameters
        ----------
        data_list : list
            List of data to be saved in the CSV file.
        title_list : list
            List of titles for the CSV columns.
        file_name : str
            The name of the CSV file to be saved.

        Returns
        -------
        str
            The path of the saved CSV file.
        """
        path_file = f"{self.path}/{file_name}.csv"
        # Transpose the list of data
        data_transposed = list(itertools.zip_longest(*data_list))
        with open(path_file, 'w', newline='', encoding='utf-8') as file_csv:
            writer = csv.writer(file_csv)
            # Write titles as the first line
            writer.writerow(title_list)
            # Write transposed data
            for row in data_transposed:
                writer.writerow(row)
        return path_file

    def add_column_to_csv(self, original_file, new_column_names, new_column_data):
        """
        Adds new columns to an existing CSV file.

        Parameters
        ----------
        original_file : str
            The name of the original CSV file.
        new_column_names : list
            List of names for the new columns to be added.
        new_column_data : list
            List of data for the new columns.

        Returns
        -------
        None
        """
        # Open the original CSV file in read mode
        original_file = f"{self.path}/{original_file}.csv"
        # Open the CSV file in read mode
        with open(original_file, 'r', encoding='utf-8') as input_file:
            # Create a CSV reader
            csv_reader = csv.reader(input_file)
            # Read existing data
            lines = list(csv_reader)
            header = lines[0]

        for title in new_column_names:
            header.append(title)

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
    # Example of using the class
    PATH = "./experiments/experiments_2023/experiments_12_2023/experiments_15_12_2023/Fente_2nm"
    transformer = CSVTransformer(PATH)
    # Call the method to save data in CSV format
    transformer.save_data_csv(data_list=[[1, 2, 3], [4, 5, 6], [1]], title_list=['Absorbance', 'Longueur d\'onde (nm)', 'C'], file_name='nom_fichier')
    # Example usage of the function
    ORIGINAL_FILE = 'nom_fichier'
    NEW_COLUMNS_NAMES = ['NewColumn1', 'NewColumn2', 'NewColumn3']
    NEW_COLUMNS_DATA = [
        ['value1', 'value2', 'value3', 'value4', 'value5'],
        ['data1', 'data2', 'data3', 'data4', 'data5'],
        ['info1', 'info2', 'info3', 'info4', 'info5']
    ]

    transformer.add_column_to_csv(ORIGINAL_FILE, NEW_COLUMNS_NAMES, NEW_COLUMNS_DATA)
