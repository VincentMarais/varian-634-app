"""
This program will create the baseline for the absorbance analysis of the sample.
"""
import time
import numpy as np
import os
from datetime import datetime, timedelta

# Motors
from kinematic_chains.motors.motors_varian_634 import GeneralMotorsController


# Voltage acquisition
from electronics_controler.ni_pci_6221 import VoltageAcquisition

# Data processing
from utils.data_csv import save_data_csv
from utils.draw_curve import graph
from utils.directory_creation import creation_directory_date_slot, get_solution_cuvette, delete_files_in_directory

class SpectroBaseline:
    def __init__(self, arduino_motors, arduino_sensors):
        self.arduino_motors = arduino_motors
        self.arduino_sensors = arduino_sensors
        self.motors_controller = GeneralMotorsController(self.arduino_motors, self.arduino_sensors)
        self.ni_pci_6221= VoltageAcquisition()
        self.path_baseline="./client/python/core/data_baseline"
    
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
        echantillon_name = input("Nom de l'espèce étudié ? ")
        [path, date, slot_size] = creation_directory_date_slot()
        self.motors_controller.initialisation_motors()

        return echantillon_name, path, date, slot_size

    def perform_step_measurement_baseline(self):
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

    def precision_mode_baseline(self, screw_travel, number_measurements):
        """
        Exécute le mode de précision pour la mesure et retourne les résultats.
        """
        choice = get_solution_cuvette()
        voltages_photodiode_1, voltages_photodiode_2 = [], []
        no_screw, wavelength = [0], []
        step = screw_travel / number_measurements
        time_per_step = (step * 60) / 10 # screw_translation_speed=10

        for i in range(1, number_measurements):
            voltage_1, voltage_2 = self.perform_step_measurement_baseline()
            voltages_photodiode_1.append(voltage_1)
            voltages_photodiode_2.append(voltage_2)
            position = i * step
            self.motors_controller.move_screw(position)
            time.sleep(time_per_step)
            no_screw.append(position)
            wavelength.append(self.calculate_wavelength(position))

        reference_solution, sample_solution = (voltages_photodiode_1, voltages_photodiode_2) if choice == 'cuve 1' else (voltages_photodiode_2, voltages_photodiode_1)
        return list(reversed(wavelength)), list(reversed(reference_solution)), list(reversed(sample_solution)), list(reversed(no_screw))

    def baseline_acquisition(self, screw_travel, number_measurements):
        """
        Effectue une acquisition complète et sauvegarde les données.
        """
        [echantillon, path, date, slot_size] = self.initialize_measurement()
        data_acquisition = self.precision_mode_baseline(screw_travel, number_measurements)
        title_data_acquisition = ["Longueur d'onde (nm)", "Tension référence (Volt)", "Tension échantillon (Volt)", "pas de vis (mm)"]
        title_file = 'baseline' + date + '_' + slot_size + '_' + echantillon
        save_data_csv(path=path, data_list=data_acquisition, title_list=title_data_acquisition, file_name=title_file)
        self.motors_controller.wait_for_idle()
        self.motors_controller.reset_screw_position()
        absorbance_baseline = np.log(data_acquisition[2]/data_acquisition[1])
        return title_file, absorbance_baseline
    
    def baseline_verification(self):
        """
        verification=Vérifie si je fichier baseline_date_heure.csv est bien créé
        
        Si verification=False
            print("Le fichier baseline_date_heure.csv n'est pas créé.")
            print("Réalisation de la baseline")
            execute baseline_acquisition
            supprime tout les anciens dans le répertoire : ./client/python/core/data_baseline

        Sinon :
            reponse=input("Souhaitez vous réaliser une nouvelle baseline, 'Oui' ou 'Non' ")
            Si reponse='Oui' :
                execute  fonction acquisition baseline
            Si reponse='Non' :

            Si reponse not in ['Oui', 'Non']:
                reponse=input("Souhaitez vous réaliser une nouvelle baseline, 'Oui' ou 'Non'")
                
        
        """
        current_date = datetime.now() 
        current_day = current_date.strftime("%d_%m_%Y")
        baseline_file= self.path_baseline + 'data_baseline_' + current_day + '.csv'
        # Vérification si le fichier baseline_date_heure.csv existe
        if not os.path.exists(baseline_file):
            print("Le fichier baseline_date_heure.csv n'est pas créé.")
            delete_files_in_directory(self.path_baseline)
            print("Réalisation de la baseline")
            self.baseline_acquisition(screw_travel=13.3, number_measurements=200)
            print("Exécution de baseline_acquisition")

        else:
            reponse = input("Souhaitez-vous réaliser une nouvelle baseline, 'Oui' ou 'Non'? ").lower()

            if reponse == 'oui':
                self.baseline_acquisition(screw_travel=13.3, number_measurements=200)
                print("Exécution de acquisition_baseline")

            elif reponse == 'non':
                pass 

            else:
                while reponse not in ['oui', 'non']:
                    reponse = input("Répondez par 'Oui' ou 'Non'. Souhaitez-vous réaliser une nouvelle baseline? ").lower()


        


# End-of-file (EOF)

