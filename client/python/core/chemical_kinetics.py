"""
"This program will perform an analysis 
of the absorbance kinetics for the absorbance 
analysis of the sample.

"""

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

from baseline_scanning import Varian634BaselineScanning

experim_manager=ExperimentManager()

class Varian634KineticsAnalysis:
    """
    Ce programme se concentrera sur 1 ou 3 longueurs d'onde 
    dans une période définie par l'utilisateur et introduira un délai entre deux mesures 
    d'absorbance lors de l'analyse de la solution.
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
        self.baseline=Varian634BaselineScanning(arduino_motors_intance, arduino_sensors_instance, mode_variable_slits)
        self.csv=CSVTransformer(self.path)
        # init digital processing
        self.noise_processing=PhotodiodeNoiseReducer()
        self.peak_search_window=1
        self.graph=Varian634ExperimentPlotter(self.path, self.echantillon_name, self.peak_search_window)


    
    

    def run_kinetics_analysis(self, time_acquisition, wavelengths, delay_between_measurements):
        if self.mode_variable_slits :
            pass
        else :
            self.baseline.initialize_measurement()

        for wavelength in wavelengths:
            course_vis = 1 / 31.10419907 * (800 - wavelength)
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
            data_acquisition = [wavelength, temps, absorbance]
            title_file = f'{self.date}_{self.slot_size}_{self.echantillon_name}_longueur_{wavelength}'
            self.csv.save_data_csv(data_acquisition, ["Longueur d'onde (nm)", "Temps (s)", "Absorbance"], title_file)
            self.motors_controller.reset_screw_position(course_vis)


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

    kinetics_mode = Varian634KineticsAnalysis(arduino_motors, arduino_sensors, MODE_SLITS)
    TIME_ACQUISITION=2
    WAVELENGTHS=[400,450,500]
    DELAY=1
    kinetics_mode.run_kinetics_analysis(TIME_ACQUISITION, WAVELENGTHS, DELAY)