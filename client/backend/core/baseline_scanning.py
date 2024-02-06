"""
This program will create the baseline for the absorbance analysis of the sample and
scan wavelengths within a specific interval to detect the peak of absorbance in the solution.


Define deferente speed of analysis 3 for exampl (look the exampl in the spectro use in TP GP3A) :
- suvey 100nm/min
- half 10nm/min
- slow 1nm/min  

Visible range with the screw pitch:
400nm -> 5.4mm and ending at 800 nm -> 18.73nm
"""
import time
import os
from datetime import datetime
import pandas as pd
import numpy as np

# Motors
from kinematic_chains.motors_varian_634 import GeneralMotorsController

# Voltage acquisition
from electronics_controler.ni_pci_6221 import VoltageAcquisition

# Data processing
from utils.data_csv import CSVTransformer
from utils.draw_curve import Varian634ExperimentPlotter
from utils.experiment_manager import ExperimentManager
from utils.digital_signal_processing import PhotodiodeNoiseReducer

experim_manager = ExperimentManager()


class Varian634BaselineScanning:
    """
    A class with all methods to do baseline and scanning.
    """

    def __init__(self, arduino_motors_instance, arduino_sensors_instance, mode_variable_slits):
        """
        Initializes the Varian634BaselineScanning class.

        Parameters:
            arduino_motors_instance: Instance representing the Arduino connected to motors.
            arduino_sensors_instance: Instance representing the Arduino connected to the fork.
            mode_variable_slits: Mode for variable slits.
        """
        # Init hardware
        self.arduino_motors = arduino_motors_instance
        self.arduino_sensors = arduino_sensors_instance
        self.mode_variable_slits = mode_variable_slits
        self.motors_controller = GeneralMotorsController(self.arduino_motors, self.arduino_sensors)
        self.daq = VoltageAcquisition()
        # Init experiment tools
        self.path_baseline = experim_manager.create_data_baseline()
        self.path, self.date, self.slot_size = experim_manager.creation_directory_date_slot()
        self.echantillon_name = input("Nom de l'espèce étudié ? ")
        self.choice = experim_manager.get_solution_cuvette()
        self.title_file = self.date + '_' + self.slot_size
        self.title_file_echantillon = self.date + '_' + self.slot_size + '_' + self.echantillon_name
        self.csv = CSVTransformer(self.path)
        # Init digital processing
        self.noise_processing = PhotodiodeNoiseReducer()
        self.peak_search_window = 1
        self.graph = Varian634ExperimentPlotter(self.path, self.echantillon_name, self.peak_search_window)


    def perform_step_measurement(self):
        """
        Performs a measurement at a given step and returns the measured voltages.
        """
        channels = ['Dev1/ai0', 'Dev1/ai1']
        #acquiere la tension aux borne de photodiode 1
        voltage_photodiode_1 = self.daq.voltage_acquisition_scanning_baseline(channels[0])
        # move mirror motor 0.333334 = 60° to switch cuvette
        self.motors_controller.move_mirror_motor(0.33334)
        # wait mirror motor 
        self.motors_controller.wait_for_idle()
        # read the voltage on photodiode 2
        voltage_photodiode_2 = self.daq.voltage_acquisition_scanning_baseline(channels[1])

        self.motors_controller.move_mirror_motor(-0.33334)

        self.motors_controller.wait_for_idle()

        return voltage_photodiode_1, voltage_photodiode_2

    def calculate_wavelength(self, position):
        """
        Calculates the wavelength based on the position.
        """
        return -31.10419907 * position + 800

    def precision_mode(self, screw_travel, number_measurements):
        """
        Executes the precision mode for the measurement and returns the results.
        """
        voltages_photodiode_1, voltages_photodiode_2 = [], []
        no_screw, wavelength = [0], []
        step = screw_travel / number_measurements        
        self.motors_controller.unlock_motors()
        # mode relatif :
        self.motors_controller.execute_g_code("G91")
        # Laissé le temps au moteurs de recevoir la commande dans le serial
        time.sleep(1)
        for i in range(1, number_measurements):
            voltage_1, voltage_2 = self.perform_step_measurement()
            # On deplace le reseau de diffraction pour 
            # changer de longueur d'onde
            self.motors_controller.move_screw(step)
            # On stoke toute les datas necessaires
            # pour tracer le graphique de l'absorbance 
            # En fonction de la longueur d'onde
            voltages_photodiode_1.append(voltage_1)
            voltages_photodiode_2.append(voltage_2)
            position = i * step
            no_screw.append(position)
            wavelength.append(self.calculate_wavelength(position))
            # On sauvegarde les datas au fur et à mesure                
            title_data_acquisition = ["Longueur d'onde (nm)", "Tension photodiode 1 (Volt)", "Tension photodiode 2 (Volt)", 
                                  "pas de vis (mm)"]
            datas = [wavelength, voltages_photodiode_1, voltages_photodiode_2, no_screw]
            title_file = "raw_data_" + self.title_file
            self.csv.save_data_csv(datas, title_data_acquisition, title_file)
            # On attend que le réseau de diffraction soit bien arrivé à la longueur d'onde souhaité
            self.motors_controller.wait_for_idle()
        # Reference and cuvette 1
        if self.choice == 'cuvette 1':
            reference_solution, sample_solution = (voltages_photodiode_1, voltages_photodiode_2)
        else:
            reference_solution, sample_solution = (voltages_photodiode_2, voltages_photodiode_1)
        reference_solution=np.array(reference_solution)
        sample_solution=np.array(sample_solution)
        absorbance = np.log10(reference_solution/sample_solution)
        return wavelength, list(absorbance)

    def acquisition(self, screw_travel, number_measurements, mode):
        """
        Performs a complete acquisition and saves the data.

        Args:
            screw_travel: Total distance the screw must travel.
            number_measurements: Total number of measurements to perform.
            mode: Mode of the acquisition.
        """
        if self.mode_variable_slits:
            pass
        else:
            self.motors_controller.initialisation_motors()
        data_acquisition = self.precision_mode(screw_travel, number_measurements)

        title_data_acquisition = ["Longueur d'onde (nm)", "Absorbance"]
        title_file = mode + self.title_file
        self.csv.save_data_csv(data_acquisition, title_data_acquisition, title_file)

        self.motors_controller.wait_for_idle()
        self.motors_controller.reset_screw_position(screw_travel)
    
        return data_acquisition

    def acquisition_baseline(self, screw_travel, number_measurements):
        """
        Performs a complete baseline acquisition and saves the data.
        """
        self.acquisition(screw_travel, number_measurements, mode='baseline')

    def baseline_verification(self):
        """
        Checks if a baseline file exists for the Varian 634 scanning mode.

        This function checks if a baseline file named 'data_baseline_DD_MM_YYYY.csv' exists
        in the specified path. If the file does not exist, it prompts the user to decide
        whether to create a new baseline by calling the 'baseline_acquisition' method. If the
        file exists, the user is given the option to create a new baseline or proceed without
        creating one.
        """
        current_date = datetime.now()
        current_day = current_date.strftime("%d_%m_%Y")
        baseline_file = self.path_baseline + 'baseline_' + current_day + '_' + self.slot_size
        # Verification if the baseline_date_heure.csv file exists
        if not os.path.exists(baseline_file):
            print('Le fichier' + baseline_file + '  n\'est pas créé.')
            experim_manager.delete_files_in_directory(self.path_baseline)
            print("Réalisation de la baseline")
            self.acquisition_baseline(13.3, 200)
            print("Exécution de baseline_acquisition")

        else:
            reponse = input("Souhaitez-vous réaliser une nouvelle baseline, 'Oui' ou 'Non'? ").lower()

            if reponse == 'oui':
                self.acquisition_baseline(13.3, 200)
                print("Exécution de acquisition_baseline")

            elif reponse == 'non':
                pass

            else:
                while reponse not in ['oui', 'non']:
                    reponse = input("Répondez par 'Oui' ou 'Non'. Souhaitez-vous réaliser une nouvelle baseline ? ").lower()
        return baseline_file

    def scanning_acquisition(self, screw_travel, number_measurements):
        """
        Performs a complete data acquisition, saves the results, and manages motor states.

        Args:
            screw_travel: Total distance the screw must travel.
            number_measurements: Total number of measurements to perform.
        """
        baseline_file = self.baseline_verification()
        data_baseline = pd.read_csv(baseline_file, encoding='ISO-8859-1')
        absorbance_baseline = data_baseline['Absorbance']
        data_acquisition=self.acquisition(screw_travel, number_measurements, 'scanning')
        wavelength = data_acquisition[0]
        absorbance_scanning = data_acquisition[1]
        absorbance = self.noise_processing.sample_absorbance(absorbance_baseline, absorbance_scanning)

        title_data_acquisition = ["Longueur d'onde (nm)", "Absorbance"]
        data_acquisition = [wavelength, absorbance]
        title_file = self.title_file + '_final'
        self.csv.save_data_csv(data_acquisition, title_data_acquisition, title_file)
        # End-of-file (EOF)


if __name__ == "__main__":
    import serial
    from pyfirmata import Arduino

    # INITIALIZATION MOTOR:

    COM_PORT_MOTORS = 'COM3'
    COM_PORT_SENSORS = 'COM9'
    BAUD_RATE = 115200
    INITIALIZATION_TIME = 2

    arduino_motors = serial.Serial(COM_PORT_MOTORS, BAUD_RATE)
    arduino_motors.write("\r\n\r\n".encode())  # encode to convert "\r\n\r\n"
    time.sleep(INITIALIZATION_TIME)  # Wait for initialization of GRBL
    arduino_motors.flushInput()  # Clear the input buffer by discarding its current contents.

    # INITIALIZATION Optical Fork:

    arduino_sensors = Arduino(COM_PORT_SENSORS)
    MODE_SLITS = False

    baseline_scanning = Varian634BaselineScanning(arduino_motors, arduino_sensors, MODE_SLITS)
    print(baseline_scanning.precision_mode(1,5))
    #baseline_scanning.scanning_acquisition(screw_travel = 2, number_measurements = 3)
