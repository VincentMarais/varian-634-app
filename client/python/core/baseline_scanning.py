"""
This program will create the baseline for the absorbance analysis of the sample and
scan wavelengths within a specific interval to detect the peak of absorbance in the solution.


Define deferente speed of analysis 3 for exampl (look the exampl in the spectro use in TP GP3A) :
- suvey 100nm/min
- half 10nm/min
- slow 1nm/min  
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

experim_manager=ExperimentManager()


class Varian634BaselineScanning:
    """
    class with all methods to do baseline and scanning
    """
    def __init__(self, arduino_motors_intance, arduino_sensors_instance, mode_variable_slits):
        # init hardware
        self.arduino_motors = arduino_motors_intance
        self.arduino_sensors = arduino_sensors_instance
        self.mode_variable_slits=mode_variable_slits
        self.motors_controller = GeneralMotorsController(self.arduino_motors, self.arduino_sensors)
        self.ni_pci_6221= VoltageAcquisition()
        # init experiment tools
        self.path_baseline="./client/python/core/data_baseline"
        self.path, self.date, self.slot_size = experim_manager.creation_directory_date_slot()
        self.echantillon_name = input("Nom de l'espèce étudié ? ")
        self.title_file = self.date + '_' + self.slot_size
        self.title_file_echantillon = self.date + '_' + self.slot_size + '_' + self.echantillon_name
        self.csv=CSVTransformer(self.path)
        # init digital processing
        self.noise_processing=PhotodiodeNoiseReducer()
        self.peak_search_window=1
        self.graph=Varian634ExperimentPlotter(self.path, self.echantillon_name, self.peak_search_window)


    def initialize_measurement(self):
        """
        Initializes the necessary components for the measurement.
        Input:
            arduino_motors (serial.Serial): Instance représentant l'Arduino connecté aux moteurs.
            arduino_sensors (pyfirmata.Arduino): Instance représentant l'Arduino connecté à la fourche
            screw_translation_speed (int): Translation speed of the screw

        Output:
            echantillon_name (string): Name of the sample that the user wants to analyze
            path (string): Working directory for the experiment
            date (string): Today's date
            slot_size (string): Size of the slot used
        """
        self.motors_controller.initialisation_motors()


    def perform_step_measurement(self):
        """
        Effectue une mesure à un pas donné et retourne les tensions mesurées.
        """
        g_code = '$X' + '\n'
        self.arduino_motors.write(g_code.encode())

        voltage_photodiode_1 = self.ni_pci_6221.voltage_acquisition_scanning_baseline(channel='ai0')

        self.motors_controller.move_mirror_motor(0.33334)
        time.sleep(1)
        voltage_photodiode_2 = self.ni_pci_6221.voltage_acquisition_scanning_baseline(channel='ai1')

        self.motors_controller.move_mirror_motor(-0.33334)
        time.sleep(1)

        return voltage_photodiode_1, voltage_photodiode_2

    def calculate_wavelength(self, position):
        """
        Calcule la longueur d'onde en fonction de la position.
        """
        return -31.10419907 * position + 800

    def precision_mode(self, screw_travel, number_measurements):
        """
        Exécute le mode de précision pour la mesure et retourne les résultats.
        """
        choice = experim_manager.get_solution_cuvette()
        voltages_photodiode_1, voltages_photodiode_2 = [], []
        no_screw, wavelength = [0], []
        step = screw_travel / number_measurements
        time_per_step = (step * 60) / 10 # screw_translation_speed=10

        for i in range(1, number_measurements):
            voltage_1, voltage_2 = self.perform_step_measurement()
            voltages_photodiode_1.append(voltage_1)
            voltages_photodiode_2.append(voltage_2)
            position = i * step
            self.motors_controller.move_screw(position)
            time.sleep(time_per_step)
            no_screw.append(position)
            wavelength.append(self.calculate_wavelength(position))
        # reference et cuve 1
        if choice == 'cuve 1' :
            reference_solution, sample_solution = (voltages_photodiode_1, voltages_photodiode_2) 
        else : 
            reference_solution, sample_solution = (voltages_photodiode_2, voltages_photodiode_1)
        return step, list(reversed(wavelength)), list(reversed(reference_solution)), list(reversed(sample_solution)), list(reversed(no_screw))

    

    def acquisition(self, screw_travel, number_measurements, mode):
        """
        Effectue une acquisition complète et sauvegarde les données.
        """
        if self.mode_variable_slits :
            pass
        else :
            self.initialize_measurement()

        self.initialize_measurement()
        data_acquisition = self.precision_mode(screw_travel, number_measurements)
        
        title_data_acquisition = ["Longueur d'onde (nm)", "Tension référence (Volt)", "Tension échantillon (Volt)", "pas de vis (mm)"]
        title_file=mode + self.title_file
        self.csv.save_data_csv(data_acquisition[1:], title_data_acquisition, title_file)
        
        self.motors_controller.wait_for_idle()
        self.motors_controller.reset_screw_position(screw_travel)
        
        step=data_acquisition[0]
        no_screw=data_acquisition[4]
        wavelength=data_acquisition[1]
        absorbance = np.log10(data_acquisition[3]/data_acquisition[2])
        return step, wavelength, no_screw, absorbance

    def acquisition_baseline(self, screw_travel, number_measurements):
        """
        Effectue une acquisition complète et sauvegarde les données.
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

        Returns:
            None        
        """
        current_date = datetime.now() 
        current_day = current_date.strftime("%d_%m_%Y")
        baseline_file= self.path_baseline + 'baseline_' + current_day + '_'+ self.slot_size+ '.csv'
        # Vérification si le fichier baseline_date_heure.csv existe
        if not os.path.exists(baseline_file):
            print("Le fichier baseline_date_heure.csv n'est pas créé.")
            experim_manager.delete_files_in_directory(self.path_baseline)
            print("Réalisation de la baseline")
            self.acquisition_baseline(screw_travel=13.3, number_measurements=200)
            print("Exécution de baseline_acquisition")

        else:
            reponse = input("Souhaitez-vous réaliser une nouvelle baseline, 'Oui' ou 'Non'? ").lower()

            if reponse == 'oui':
                self.acquisition_baseline(screw_travel=13.3, number_measurements=200)
                print("Exécution de acquisition_baseline")

            elif reponse == 'non':
                pass 

            else:
                while reponse not in ['oui', 'non']:
                    reponse = input("Répondez par 'Oui' ou 'Non'. Souhaitez-vous réaliser une nouvelle baseline? ").lower()
        return baseline_file

    def scanning_acquisition(self, screw_travel, number_measurements):
        """
        Effectue une acquisition complète de données, sauvegarde les résultats et gère les états du moteur.

        Args:
            arduino_motors (serial.Serial): Interface de communication avec les moteurs Arduino.
            arduino_sensors (serial.Serial): Interface de communication avec les capteurs Arduino.
            screw_travel (float): Distance totale que la vis doit parcourir.
            number_measurements (int): Nombre total de mesures à effectuer.
            screw_translation_speed (int): Vitesse de déplacement de la vis.
            pulse_frequency (float): Fréquence de la forme d'onde carrée pour la stimulation.
            duty_cycle (float): Rapport cyclique de la forme d'onde carrée.
            samples_per_channel (int): Nombre d'échantillons par canal à mesurer.
            sample_rate (int): Fréquence d'échantillonnage des mesures.
            channels (list): Liste des canaux utilisés pour la mesure.
        """
        

        baseline_file=self.baseline_verification()
        data_baseline = pd.read_csv(baseline_file, encoding='ISO-8859-1')
        absorbance_baseline = data_baseline['Absorbance']
        [step, wavelength, no_screw, absorbance_scanning]=self.acquisition(screw_travel, number_measurements, 'scanning')
        
        absorbance = self.noise_processing.sample_absorbance(absorbance_baseline, absorbance_scanning, step)

        title_data_acquisition = ["Longueur d'onde (nm)", "Absorbance", "pas de vis (mm)"]
        data_acquisition = [wavelength, absorbance, no_screw]
        title_file= self.title_file + '_final'
        self.csv.save_data_csv(data_acquisition, title_data_acquisition, title_file)
        # End-of-file (EOF)

if __name__ == "__main__":
    import serial
    from pyfirmata import Arduino

    # INITIALISATION MOTEUR:

    COM_PORT_MOTORS = 'COM3'
    COM_PORT_SENSORS = 'COM9'
    BAUD_RATE = 115200
    INITIALIZATION_TIME = 2

    arduino_motors = serial.Serial(COM_PORT_MOTORS, BAUD_RATE)
    arduino_motors.write("\r\n\r\n".encode()) # encode pour convertir "\r\n\r\n" 
    time.sleep(INITIALIZATION_TIME)   # Attend initialisation un GRBL
    arduino_motors.flushInput()  # Vider le tampon d'entrée, en supprimant tout son contenu.

    # INITIALISATION Forche optique:

    arduino_sensors = Arduino(COM_PORT_SENSORS)
    MODE_SLITS = False

    baseline_scanning = Varian634BaselineScanning(arduino_motors, arduino_sensors, MODE_SLITS)
    baseline_scanning.scanning_acquisition(screw_travel=2, number_measurements=3)
