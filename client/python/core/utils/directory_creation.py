import os
import datetime

class ExperimentManager:
    def __init__(self):
        pass

    @staticmethod
    def detection_existence_directory(path):
        """
        Check if the directory exists
        """
        path = os.path.join(path)
        return os.path.exists(path)

    @staticmethod
    def create_directory(path):
        """
        Create the directory if it doesn't exist
        """
        if not ExperimentManager.detection_existence_directory(path):
            os.makedirs(path)
            print("Directory created successfully:", path)
        else:
            print("Directory already exists:", path)

    @staticmethod
    def directory_year_month_day():
        """
        Create a directory with the current year_month_day
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
        """
        slot_size = input("Slot size: Fente_2nm, Fente_1nm, Fente_0_5nm, Fente_0_2nm: ")
        date_today = datetime.date.today()
        date_str = date_today.strftime("%d_%m_%Y")
        path = ExperimentManager.directory_year_month_day()
        path = os.path.join(path, slot_size)
        ExperimentManager.create_directory(path)
        return path, date_str, slot_size

    @staticmethod
    def path_creation(path, physical_data):
        """
        Create a path for physical data
        """
        chemin = os.path.join(path, physical_data)
        ExperimentManager.create_directory(chemin)
        return chemin

    @staticmethod
    def get_solution_cuvette():
        """
        Ask the user in which cuvette they placed the reference
        """
        solution = input("In which cuvette number is the blank solution: cuvette 1 or cuvette 2: ")
        while solution not in ['cuvette 1', 'cuvette 2']:
            solution = input("Please choose cuvette 1 or cuvette 2: ")
        print("The blank solution is in", solution)
        return solution

    @staticmethod
    def delete_files_in_directory(directory_path):
        """
        Delete all files in a given directory
        """
        with os.scandir(directory_path) as entries:
            for entry in entries:
                if entry.is_file():
                    os.remove(entry.path)


    @staticmethod
    def validate_user_input(prompt, valid_responses):
        response = input(prompt)
        while response not in valid_responses:
            response = input(prompt)
        return response
    
    def wait_for_user_confirmation(self, prompt):
        while input(prompt) != 'Oui':
            pass