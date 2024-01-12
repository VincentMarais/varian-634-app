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
from chemical_kinetics import SpectroKineticsAnalysis

experim_manager=ExperimentManager()

class SpectroVariableSlits:
    """
    Ce programme executera les en faisant varier la fente variable
    """
    def __init__(self, arduino_motors, arduino_sensors):
        self.arduino_motors = arduino_motors
        self.arduino_sensors = arduino_sensors
        self.motors_controller = GeneralMotorsController(self.arduino_motors, self.arduino_sensors)
        self.ni_pci_6221= VoltageAcquisition()

        self.baseline_scanning=SpectroBaselineScanning(self.arduino_motors, self.arduino_sensors)
        self.path_baseline="./client/python/core/data_baseline"
        self.chemical_kinetics=SpectroKineticsAnalysis(self.arduino_motors, self.arduino_sensors)

        self.path, self.date, self.slot_size = experim_manager.creation_directory_date_slot()
        self.echantillon_name = input("Nom de l'espèce étudié ? ")
        self.title_file = self.date + '_' + self.slot_size
        self.title_file_echantillon = self.date + '_' + self.slot_size + '_' + self.echantillon_name

        self.noise_processing=PhotodiodeNoiseReducer()
        self.peak_search_window=1
        
        self.graph=Varian634ExperimentPlotter(self.path, self.echantillon_name, self.peak_search_window)

        self.csv=CSVTransformer(self.path)

        self.slits_position=[1,2,3,4]

    
    def slit_variable_scanning(self, screw_travel, number_measurements):
        for slits in self.slits_position:
            self.motors_controller.move_slits(slits)
            self.motors_controller.wait_for_idle()
            self.baseline_scanning.scanning_acquisition(screw_travel, number_measurements)

    def slit_variable_chemical_kinetics(self, time_acquisition, longueurs_a_analyser, delay_between_measurements):
        
        for slits in self.slits_position:
            self.motors_controller.move_slits(slits)
            self.motors_controller.wait_for_idle()
            self.chemical_kinetics.run_kinetics_analysis(time_acquisition, longueurs_a_analyser, delay_between_measurements)
        


# Usage
# analyzer = ChemicalKineticsAnalyzer(arduino_motors, arduino_sensors)
# analyzer.run_analysis(temps_d_acquisition, longueurs_a_analyser, samples_per_channel, sample_rate, square_wave_frequency, channels, delay_between_measurements)
