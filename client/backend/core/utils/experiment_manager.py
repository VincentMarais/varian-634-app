"""
This program provides user assistance for VARIAN 634 experiments.

"""

import os
import datetime

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
        pass

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

    @staticmethod
    def directory_year_month_day():
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
            "./experiments",
            "experiments_" + current_year,
            "experiments_" + current_month,
            "experiments_" + current_day)
        ExperimentManager.create_directory(path)
        return path

    @staticmethod
    def creation_directory_date_slot():
        """
        Create a directory with the length of the slot used in the experiment.

        Returns
        -------
        tuple
            A tuple containing path, date_str, and slot_size.
        """
        slot_size = ExperimentManager.validate_user_input(
            "Slot size: Fente_2nm, Fente_1nm, Fente_0_5nm, Fente_0_2nm: ",
            ['Fente_2nm', 'Fente_1nm', 'Fente_0_5nm', 'Fente_0_2nm']
        )
        date_today = datetime.date.today()
        date_str = date_today.strftime("%d_%m_%Y")
        path = ExperimentManager.directory_year_month_day()
        path = os.path.join(path, slot_size)
        ExperimentManager.create_directory(path)
        return path, date_str, slot_size

    @staticmethod
    def path_creation(path, physical_data):
        """
        Create a path for physical data.

        Parameters
        ----------
        path : str
            The base path.
        physical_data : str
            The physical data.

        Returns
        -------
        str
            The created path.
        """
        chemin = os.path.join(path, physical_data)
        ExperimentManager.create_directory(chemin)
        return chemin

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
    ExperimentManager().create_data_baseline()
