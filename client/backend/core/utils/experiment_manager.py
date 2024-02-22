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

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
import pandas as pd


class ExperimentManager:
    """
    A class to manage and analyze experimental data, including file management, data visualization, and user interaction.
    """

    def __init__(self, sample_analyzed_name):
        """
        Initializes the ExperimentManager with the name of the chemical species being analyzed.

        Args:
            sample_analyzed_name (str): The name of the chemical species analyzed in the experiments.
        """
        self.sample_analyzed_name = sample_analyzed_name
    
    def save_data_csv(self, path, data_list, title_list, file_name):
        """
        Transforms and saves the provided data to a CSV file.

        Args:
            path (str): The directory path where the CSV file will be saved.
            data_list (list): List of data rows to be saved in the CSV file.
            title_list (list): List of column titles for the CSV.
            file_name (str): The name for the CSV file.

        Returns:
            path_file (str): The full path of the saved CSV file.
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

    def detection_existence_directory(self, path):
        """
        Checks if the specified directory exists.

        Args:
            path (str): The path to the directory to check.

        Returns:
            bool: True if the directory exists, False otherwise.
        """
        path = os.path.join(path)
        return os.path.exists(path)

    def create_directory(self, path):
        """
        Creates a directory at the specified path if it doesn't exist.

        Args:
            path (str): The path where the directory will be created.

        Returns:
            None
        """
        if not self.detection_existence_directory(path):
            os.makedirs(path)
            print("Directory created successfully:", path)
        else:
            print("Directory already exists:", path)

    def directory_year_month_day(self, path):
        """
        Creates a directory structure based on the current year, month, and day.

        Args:
            path (str): The base path where the new directory structure will be created.

        Returns:
            str: The path of the newly created directory.
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
        Creates a directory named after the current date and the slot size used in the experiment.

        Args:
            path (str): The base path where the new directory will be created.

        Returns:
            tuple: Contains the path, date string, and slot size.
        """
        path = self.directory_year_month_day(path)
        slot_size = self.validate_user_input(
            "Slot size: Fente_2nm, Fente_1nm, Fente_0_5nm, Fente_0_2nm: ",
            ['Fente_2nm', 'Fente_1nm', 'Fente_0_5nm', 'Fente_0_2nm']
        )
        date_today = datetime.date.today()
        date_str = date_today.strftime("%d_%m_%Y")
        path = os.path.join(path, slot_size)
        self.create_directory(path)
        return path, date_str, slot_size

    @staticmethod
    def get_solution_cuvette():
        """
        Prompts the user to specify the cuvette containing the reference solution.

        Returns:
            str: The cuvette number chosen by the user.
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
        Deletes all files within the specified directory.

        Args:
            directory_path (str): The path to the directory from which files will be deleted.

        Returns:
            None
        """
        with os.scandir(directory_path) as entries:
            for entry in entries:
                if entry.is_file():
                    os.remove(entry.path)

    @staticmethod
    def validate_user_input(prompt, valid_responses):
        """
        Validates user input against a list of valid responses.

        Args:
            prompt (str): The message displayed to the user.
            valid_responses (list): A list of acceptable responses.

        Returns:
            str: The validated user input.
        """
        response = input(prompt)
        while response not in valid_responses:
            response = input(prompt)
        return response 

    
    def choose_folder(self, root):
        """
        Prompts the user to select a folder where they wish to save their file.

        Args:
            root (tk.Tk): The root Tkinter window.

        Returns:
            str: The path of the selected folder.
        """
        
        # Hide the main window (do not use it)
        root.iconify()
        # Open the folder selection dialog and store the selected folder path
        folder = filedialog.askdirectory()

        root.destroy()
        # Return the folder path
        return folder

    def wait_for_user_confirmation(self, prompt):
        """
        Pauses program execution until the user confirms by inputting 'Oui'.

        Args:
            prompt (str): The message displayed to the user.

        Returns:
            None
        """
        while input(prompt) != 'Oui':
            pass

    def link_cuvette_voltage(choice, voltages_photodiode_1, voltages_photodiode_2):
        """
        Lie le choix de cuvette de l'utilisateur à la photodiode
            Si l'utilisateur à mis l'échantillon dans la cuvette 1 alors 
            la tension mesurer par la photodiode 1 sera celle de l'échantillon
        """

        if choice == 'cuvette 1':
            reference_solution, sample_solution = (voltages_photodiode_1, voltages_photodiode_2)
        else:
            reference_solution, sample_solution = (voltages_photodiode_2, voltages_photodiode_1)
        
        return reference_solution, sample_solution
    def max_absorbance_display(self, wavelength_peak, absorbance_peak, wavelength, absorbance):
        """
        Displays the absorbance peak and maximum absorbance on a plot.

        Args:
            wavelength_peak (float): The wavelength at the maximum absorbance peak.
            absorbance_peak (float): The maximum absorbance value.
            wavelength (numpy.ndarray): The array of wavelengths.
            absorbance (numpy.ndarray): The array of absorbance values.

        Returns:
            None
        """
        plt.scatter(wavelength_peak, absorbance_peak, color='red')

        plt.annotate(f'({wavelength_peak:.2f} nm, {absorbance_peak:.2f})',
                     xy=(wavelength_peak, absorbance_peak),
                     xytext=(wavelength_peak + 10, absorbance_peak),
                     fontsize=10,
                     color='red',
                     arrowprops=dict(facecolor='red', arrowstyle='->'))

        plt.hlines(y=absorbance_peak,
                   xmin=wavelength[0],
                   xmax=wavelength_peak,
                   linestyle='dashed',
                   color='red')

        plt.vlines(x=wavelength_peak, ymin=min(absorbance),
                   ymax=absorbance_peak,
                   linestyle='dashed',
                   color='red')
        

    def extract_data_csv(self, path, file_experiment, name_data_x, name_data_y):
        """
        Extracts X and Y data from a CSV file.

        Args:
            path (str): The directory path where the CSV file is located.
            file_experiment (str): The name of the experiment file.
            name_data_x (str): The column name for the X data.
            name_data_y (str): The column name for the Y data.

        Returns:
            tuple: Contains the X data (as a pandas Series) and Y data (as a pandas Series).
        """
        path_file = f"{path}/{file_experiment}.csv"
        data_file_experiment = pd.read_csv(path_file, encoding='ISO-8859-1')

        data_x = data_file_experiment[name_data_x]
        data_y = data_file_experiment[name_data_y]

        return data_x, data_y

    def graph_absorbance(self, path, name_data_x, file_experiment, peak_search_window):
        """
        Plots the absorbance as a function of wavelength from experimental data and highlights the absorbance peaks.

        Args:
            path (str): The directory path where the data files are located.
            name_data_x (str): The column name for the X data (wavelength).
            file_experiment (str): The name of the experiment file.
            peak_search_window (int): The window size for peak detection.

        Returns:
            None
        """

        [wavelength, absorbance] = self.extract_data_csv(path, file_experiment, name_data_x, 'Absorbance')
        absorbance_peak = max(absorbance)
        wavelength_peak = wavelength[np.argmax((absorbance))]
        peaks, _ = find_peaks(absorbance, distance=peak_search_window)
        titles_data = ['Longueur d\'onde (nm)','Absorbace', "Absorbance pics", "Longueur d'onde pics (nm)"]
        data = [wavelength, absorbance, peaks, wavelength[peaks]]
        self.save_data_csv(path, data, titles_data, file_experiment)
        title_graph = 'Absorbance du ' + self.sample_analyzed_name
        plt.plot(wavelength, absorbance)
        plt.plot(wavelength[peaks], absorbance[peaks], 'ro')

        plt.xlabel('Longueur d\'onde (nm)')
        plt.ylabel('Absorbance')
        plt.title(title_graph)
        self.max_absorbance_display(wavelength_peak, absorbance_peak, wavelength, absorbance)
        plt.savefig(path + '\\' + file_experiment + ".pdf")
        plt.show()

    def save_display(self, path_file, file_experiment, name_data_x, name_data_y, title_graph):
        """
        Saves a graph of data_x and data_y in a PDF file.

        Args:
            path_file (str): The directory path where the PDF file will be saved.
            file_experiment (str): The name of the experiment file.
            name_data_x (str): The column name for the X data.
            name_data_y (str): The column name for the Y data.
            title_graph (str): The title of the graph.

        Returns:
            None
        """
        plt.figure()
        [data_x, data_y] = self.extract_data_csv(path_file, file_experiment, name_data_x, name_data_y)
        plt.plot(data_x, data_y, '-', label= name_data_y)
        plt.legend()
        plt.xlabel(name_data_x)
        plt.ylabel(name_data_y)
        plt.title(title_graph)
        plt.savefig(path_file + '\\' + file_experiment + ".pdf")

    def classic_graph(self, path_file, file_experiment, name_data_x, name_data_y, title_graph):
        """
        Plots a classic graph of the specified data.

        Args:
            path_file (str): The directory path where the data files are located.
            file_experiment (str): The name of the experiment file.
            name_data_x (str): The column name for the X data.
            name_data_y (str): The column name for the Y data.
            title_graph (str): The title of the graph.

        Returns:
            None
        """
        self.save_display(path_file, file_experiment, name_data_x, name_data_y, title_graph)
        plt.show()

if __name__ == "__main__":
    # Exemple d'utilisation:
    SAMPLE_NAME = "Bromo"
    WINDOW = 2
    experiment_manager = ExperimentManager(SAMPLE_NAME)
    ROOT = tk.Tk()
    #experiment_manager.creation_directory_date_slot()
    PATH = experiment_manager.choose_folder(ROOT)
    [PATH, DATE, SLOT_SIZE] = experiment_manager.creation_directory_date_slot(PATH)
    print([PATH, DATE, SLOT_SIZE])
    experiment_manager.save_data_csv(path = PATH, data_list=[[1, 2, 3], [4, 5, 6], [1], [23,5,5,4,3,1]], title_list=['Absorbance', 'Longueur d\'onde (nm)', 'C', "Temps (s)"], file_name='nom_fichier')
    experiment_manager.classic_graph(PATH, 'nom_fichier', "Temps (s)", 'Absorbance', "Cinétique_test")
    experiment_manager.graph_absorbance(PATH, "Longueur d'onde (nm)", 'nom_fichier', WINDOW)

    PATH = "C:\\Users\\admin\\Desktop\\GitHub\\varian-634-app\\experiments\\experiments_2024\\experiments_02_2024\\experiments_16_02_2024\\Calibrage"
    file = f"{PATH}/{'calibrage_16_02_2024_fente_2nm'}.csv"
    data = pd.read_csv(file, encoding='ISO-8859-1')
    voltage_1 = data["Tension photodiode 1 (Volt)"]
    voltage_2 = data["Tension photodiode 2 (Volt)"]
    screw = data["pas de vis (mm)"]
    plt.plot(screw, -voltage_1, label='Tension photodiode 1', linewidth=2, color='orange')
    plt.plot(screw, -voltage_2, label='Tension photodiode 2', linestyle='-', linewidth=2, color='red')
    plt.legend()
    plt.grid(True)
    plt.title('Spectre en intensité du Xe')
    plt.xlabel("pas de vis (mm)")
    plt.ylabel('Tension (Volt)')
    plt.show()



    
