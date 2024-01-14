"""
"This program will perform an analysis 
of the absorbance kinetics for the absorbance 
analysis of the sample."""


# Motors
from kinematic_chains.motors.motors_varian_634 import GeneralMotorsController

# Voltage acquisition
from electronics_controler.ni_pci_6221 import VoltageAcquisition

# Data processing
from utils.data_csv import CSVTransformer
from utils.draw_curve import Varian634ExperimentPlotter
from utils.experiment_manager import ExperimentManager
from utils.digital_signal_processing import PhotodiodeNoiseReducer

from baseline_scanning import SpectroBaselineScanning
from chemical_kinetics import SpectroKineticsAnalysis

experim_manager=ExperimentManager()

class SpectroVariableSlits:
    """
    Ce programme executera les en faisant varier la fente variable
    """
    def __init__(self, arduino_motors_intance, arduino_sensors_instance):
        # init hardware
        self.arduino_motors = arduino_motors_intance
        self.arduino_sensors = arduino_sensors_instance
        self.mode_variable_slits=True
        self.motors_controller = GeneralMotorsController(self.arduino_motors, self.arduino_sensors)
        self.slits_position=[1,2,3,4]
        self.ni_pci_6221= VoltageAcquisition()
        # init experiment tools
        self.baseline_scanning=SpectroBaselineScanning(self.arduino_motors, self.arduino_sensors, self.mode_variable_slits)
        self.path_baseline="./client/python/core/data_baseline"
        self.chemical_kinetics=SpectroKineticsAnalysis(self.arduino_motors, self.arduino_sensors, self.mode_variable_slits)
        self.path, self.date, self.slot_size = experim_manager.creation_directory_date_slot()
        self.echantillon_name = input("Nom de l'espèce étudié ? ")
        self.title_file = self.date + '_' + self.slot_size
        self.title_file_echantillon = self.date + '_' + self.slot_size + '_' + self.echantillon_name
        self.csv=CSVTransformer(self.path)
        # init digital processing
        self.noise_processing=PhotodiodeNoiseReducer()
        self.peak_search_window=1
        self.graph=Varian634ExperimentPlotter(self.path, self.echantillon_name, self.peak_search_window)       

    
    def slits_variable_scanning(self, screw_travel, number_measurements):
        """
        Programme qui balaye l'ensemble des fentes du 
        Varian durant le mode sanning
        """
        self.motors_controller.initialisation_motors()
        for slits in self.slits_position:
            self.motors_controller.move_slits(slits)
            self.motors_controller.wait_for_idle()
            self.baseline_scanning.scanning_acquisition(screw_travel, number_measurements)

    def slits_variable_chemical_kinetics(self, time_acquisition, wavelengths, delay_between_measurements):
        """
        Programme qui balaye l'ensemble des fentes du 
        Varian durant le mode analyse cinétique
        """
        self.motors_controller.initialisation_motors()
        for slits in self.slits_position:
            self.motors_controller.move_slits(slits)
            self.motors_controller.wait_for_idle()
            self.chemical_kinetics.run_kinetics_analysis(time_acquisition, wavelengths, delay_between_measurements)
        


if __name__ == "__main__":
    import serial
    from pyfirmata import Arduino
    import time

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

    slits_mode=SpectroVariableSlits(arduino_motors, arduino_sensors)
    TIME_ACQUISITION=2
    WAVELENGTHS=[400,450,500]
    DELAY=1
    slits_mode.slits_variable_chemical_kinetics(TIME_ACQUISITION, WAVELENGTHS, DELAY)