"""
This program provides user assistance for VARIAN 634 experiments.

1) Program manage CSV data of VARIAN 634 in acquisition

2) Program for graphics.


"""

import os
import datetime
import csv
import itertools

import tkinter as tk
from tkinter import filedialog

class ExperimentManager:
    """
    A class to manage experiments.

    ...

    Methods
    -------
    detection_existence_directory(path):
        Check if the directory exists.

    create_directory(path):
        Create the directory if it doesn't exist.

    directory_year_month_day():
        Create a directory with the current year_month_day.

    creation_directory_date_slot():
        Create a directory with the length of the slot used in the experiment.

    path_creation(path, physical_data):
        Create a path for physical data.

    get_solution_cuvette():
        Ask the user in which cuvette they placed the reference.

    delete_files_in_directory(directory_path):
        Delete all files in a given directory.

    validate_user_input(prompt, valid_responses):
        Validate user input.

    wait_for_user_confirmation(prompt):
        Wait for user confirmation.
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the CSVTransformer object.

        Parameters
        ----------
        path : str
            The path where the CSV files are located.
        sample_analyzed_name (str): Le nom de l'espèce chimique analysée.
        peak_search_window (int): La fenêtre de recherche des pics.
        """
        pass
    
    def save_data_csv(self, path, data_list, title_list, file_name):
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
        path_file = f"{path}/{file_name}.csv"
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

    @staticmethod
    def detection_existence_directory(path):
        """
        Check if the directory exists.

        Parameters
        ----------
        path : str
            The path to the directory.

        Returns
        -------
        bool
            True if the directory exists, False otherwise.
        """
        path = os.path.join(path)
        return os.path.exists(path)

    @staticmethod
    def create_directory(path):
        """
        Create the directory if it doesn't exist.

        Parameters
        ----------
        path : str
            The path to the directory.

        Returns
        -------
        None
        """
        if not ExperimentManager.detection_existence_directory(path):
            os.makedirs(path)
            print("Directory created successfully:", path)
        else:
            print("Directory already exists:", path)

    def directory_year_month_day(self, path):
        """
        Create a directory with the current year_month_day.

        Returns
        -------
        str
            The path of the created directory.
        """
        current_date = datetime.datetime.now()
        current_year = current_date.strftime("%Y")
        current_month = current_date.strftime("%m_%Y")
        current_day = current_date.strftime("%d_%m_%Y")        
        path = os.path.join(
            path,
            "experiments_" + current_year,
            "experiments_" + current_month,
            "experiments_" + current_day)
        self.create_directory(path)
        return path

    def creation_directory_date_slot(self, path):
        """
        Create a directory with the length of the slot used in the experiment.

        Returns
        -------
        tuple
            A tuple containing path, date_str, and slot_size.
        """
        path = self.directory_year_month_day(path)
        slot_size = self.validate_user_input(
            "Slot size: Fente_2nm, Fente_1nm, Fente_0_5nm, Fente_0_2nm: ",
            ['Fente_2nm', 'Fente_1nm', 'Fente_0_5nm', 'Fente_0_2nm']
        )
        date_today = datetime.date.today()
        date_str = date_today.strftime("%d_%m_%Y")
        path = os.path.join(path, slot_size)
        ExperimentManager.create_directory(path)
        return path, date_str, slot_size

    @staticmethod
    def get_solution_cuvette():
        """
        Ask the user in which cuvette they placed the reference.

        Returns
        -------
        str
            The cuvette number.
        """
        solution = ExperimentManager.validate_user_input(
            "In which cuvette number is the blank solution: cuvette 1 or cuvette 2: ",
            ['cuvette 1', 'cuvette 2']
        )
        print("The blank solution is in", solution)
        return solution

    @staticmethod
    def delete_files_in_directory(directory_path):
        """
        Delete all files in a given directory.

        Parameters
        ----------
        directory_path : str
            The path to the directory.

        Returns
        -------
        None
        """
        with os.scandir(directory_path) as entries:
            for entry in entries:
                if entry.is_file():
                    os.remove(entry.path)

    @staticmethod
    def validate_user_input(prompt, valid_responses):
        """
        Validate user input.

        Parameters
        ----------
        prompt : str
            The prompt message.
        valid_responses : list
            List of valid responses.

        Returns
        -------
        str
            The validated user input.
        """
        response = input(prompt)
        while response not in valid_responses:
            response = input(prompt)
        return response 

    
    def choose_folder(self):
        """
        Fonction qui permet de demander à l'utilisateur on il souhaite enregistrer son fichier
        """
        # Create an instance of Tk
        root = tk.Tk()
        # Hide the main window (do not use it)
        root.withdraw()
        # Open the folder selection dialog and store the selected folder path
        folder = filedialog.askdirectory()
        # Return the folder path
        return folder

    def wait_for_user_confirmation(self, prompt):
        """
        Wait for user confirmation.

        Parameters
        ----------
        prompt : str
            The prompt message.

        Returns
        -------
        None
        """
        while input(prompt) != 'Oui':
            pass


    @staticmethod
    def create_data_baseline():
        """        
        Display the full path of a file up
        """
        script_root = os.path.dirname(os.path.abspath(__file__))

        # Create the target directory path
        target_directory = os.path.join(script_root, 'databaseline')

        # Check if the directory exists, and create it if not
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
            print(f"Directory '{target_directory}' created.")
        else:
            print(f"Directory '{target_directory}' already exists.") 

        return target_directory




if __name__ == "__main__":
    # Exemple d'utilisation:
    SAMPLE_NAME = "Bromo"
    WINDOW = 2
    experiment_manager = ExperimentManager()
    #experiment_manager.creation_directory_date_slot()
    [path, date_str, slot_size] = experiment_manager.creation_directory_date_slot()
    print(path)
    experiment_manager.save_data_csv(path = path, data_list=[[1, 2, 3], [4, 5, 6], [1]], title_list=['Absorbance', 'Longueur d\'onde (nm)', 'C'], file_name='nom_fichier')

 



    
