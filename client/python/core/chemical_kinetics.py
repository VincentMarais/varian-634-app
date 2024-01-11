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
from utils.data_csv import save_data_csv
from utils.draw_curve import graph
from utils.directory_creation import ExperimentManager
from utils.digital_signal_processing.interpolation import sample_absorbance

from baseline import SpectroBaseline

experim_manager=ExperimentManager()

class SpectroKineticsAnalysis:
    """
    Ce programme se concentrera sur 1 ou 3 longueurs d'onde 
    dans une période définie par l'utilisateur et introduira un délai entre deux mesures 
    d'absorbance lors de l'analyse de la solution.
    """
    def __init__(self, arduino_motors, arduino_sensors):
        self.arduino_motors = arduino_motors
        self.arduino_sensors = arduino_sensors
        self.motors_controller = GeneralMotorsController(self.arduino_motors, self.arduino_sensors)
        self.ni_pci_6221= VoltageAcquisition()
        self.path_baseline="./client/python/core/data_baseline"
        self.baseline=SpectroBaseline(self.arduino_motors, self.arduino_sensors)
    
    

    def run_analysis(self, time_acquisition, longueurs_a_analyser, delay_between_measurements):
        [echantillon, path, date, slot_size] = self.baseline.initialize_measurement()

        for longueur_d_onde in longueurs_a_analyser:
            course_vis = 1 / 31.10419907 * (800 - longueur_d_onde)
            self.motors_controller.move_screw(course_vis)
            self.motors_controller.wait_for_motor_idle(self.arduino_motors)

            choice = experim_manager.get_solution_cuvette()
            self.motors_controller.wait_for_idle()

            cuvette_prompt = "Avez-vous mis votre solution dans la cuve appropriée ? "
            experim_manager.wait_for_user_confirmation(cuvette_prompt)
            channel="ai0" if choice == "cuve 1" else "ai1"
            tension_blanc = self.ni_pci_6221.voltage_acquisition_scanning_baseline(channel)
            self.motors_controller.move_mirror_cuves_motor(0.33334)

            tensions_echantillon = []
            temps = []

            self.ni_pci_6221.voltage_acquisition_chemical_kinetics(channel, time_acquisition, delay_between_measurements)

            self.motors_controller.move_mirror_cuves_motor(0.33334)

            absorbance = np.log(np.array(tensions_echantillon) / tension_blanc)
            data_acquisition = [longueur_d_onde, temps, absorbance]
            title_file = f'{date}_{slot_size}_{echantillon}_longueur_{longueur_d_onde}'
            save_data_csv(path, data_acquisition, ["Longueur d'onde (nm)", "Temps (s)", "Absorbance"], title_file)
            self.motors_controller.reset_screw_position(course_vis)

# Usage
# analyzer = ChemicalKineticsAnalyzer(arduino_motors, arduino_sensors)
# analyzer.run_analysis(temps_d_acquisition, longueurs_a_analyser, samples_per_channel, sample_rate, square_wave_frequency, channels, delay_between_measurements)
