"""
"This program will perform an analysis 
of the absorbance kinetics for the absorbance 
analysis of the sample."""

import numpy as np

# Motors
from kinematic_chains.motors.motors_varian_634 import GeneralMotorsController

# Voltage acquisition
from electronics_controler.ni_pci_6221 import VoltageAcquisition

# Data processing
from utils.data_csv import CSVTransformer
from utils.draw_curve import Varian634ExperimentPlotter
from utils.experiment_manager import ExperimentManager
from utils.digital_signal_processing.noise_processing import PhotodiodeNoiseReducer

from baseline_scanning import SpectroBaselineScanning

experim_manager=ExperimentManager()

class SpectroKineticsAnalysis:
    """
    Ce programme se concentrera sur 1 ou 3 longueurs d'onde 
    dans une période définie par l'utilisateur et introduira un délai entre deux mesures 
    d'absorbance lors de l'analyse de la solution.
    """
    def __init__(self, arduino_motors, arduino_sensors, mode_variable_slits):
        self.mode_variable_slits=mode_variable_slits
        self.arduino_motors = arduino_motors
        self.arduino_sensors = arduino_sensors
        self.motors_controller = GeneralMotorsController(self.arduino_motors, self.arduino_sensors)
        self.ni_pci_6221= VoltageAcquisition()

        self.baseline=SpectroBaselineScanning(self.arduino_motors, self.arduino_sensors, self.mode_variable_slits)
        self.path_baseline="./client/python/core/data_baseline"

        self.path, self.date, self.slot_size = experim_manager.creation_directory_date_slot()
        self.echantillon_name = input("Nom de l'espèce étudié ? ")
        self.title_file = self.date + '_' + self.slot_size
        self.title_file_echantillon = self.date + '_' + self.slot_size + '_' + self.echantillon_name

        self.noise_processing=PhotodiodeNoiseReducer()
        self.peak_search_window=1
        
        self.graph=Varian634ExperimentPlotter(self.path, self.echantillon_name, self.peak_search_window)

        self.csv=CSVTransformer(self.path)

    
    

    def run_kinetics_analysis(self, time_acquisition, longueurs_a_analyser, delay_between_measurements, mode_variable_slits):
        if mode_variable_slits :
            pass
        else :
            self.baseline.initialize_measurement()

        for longueur_d_onde in longueurs_a_analyser:
            course_vis = 1 / 31.10419907 * (800 - longueur_d_onde)
            self.motors_controller.move_screw(course_vis)
            self.motors_controller.wait_for_idle()

            choice = experim_manager.get_solution_cuvette()
            self.motors_controller.wait_for_idle()

            cuvette_prompt = "Avez-vous mis votre solution dans la cuve appropriée ? "
            experim_manager.wait_for_user_confirmation(cuvette_prompt)
            channel="ai0" if choice == "cuve 1" else "ai1"
            tension_blanc = self.ni_pci_6221.voltage_acquisition_scanning_baseline(channel)
            self.motors_controller.move_mirror_motor(0.33334)

            tensions_echantillon = []
            temps = []

            self.ni_pci_6221.voltage_acquisition_chemical_kinetics(channel, time_acquisition, delay_between_measurements)

            self.motors_controller.move_mirror_motor(-0.33334)

            absorbance = np.log(np.array(tensions_echantillon) / tension_blanc)
            data_acquisition = [longueur_d_onde, temps, absorbance]
            title_file = f'{self.date}_{self.slot_size}_{self.echantillon_name}_longueur_{longueur_d_onde}'
            self.csv.save_data_csv(data_acquisition, ["Longueur d'onde (nm)", "Temps (s)", "Absorbance"], title_file)
            self.motors_controller.reset_screw_position(course_vis)


# Usage
# analyzer = ChemicalKineticsAnalyzer(arduino_motors, arduino_sensors)
# analyzer.run_analysis(temps_d_acquisition, longueurs_a_analyser, samples_per_channel, sample_rate, square_wave_frequency, channels, delay_between_measurements)
