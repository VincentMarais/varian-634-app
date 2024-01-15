"""
This program will perform an analysis 
of the absorbance kinetics for the absorbance 
analysis of the sample.
"""

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
from chemical_kinetics import Varian634KineticsAnalysis

experim_manager = ExperimentManager()

class SpectroVariableSlits:
    """
    A class to perform absorbance kinetics analysis with variable slits.

    ...

    Attributes
    ----------
    arduino_motors : serial.Serial
        Instance of serial connection for motor control
    arduino_sensors : pyfirmata.Arduino
        Instance of Arduino for sensor control
    mode_variable_slits : bool
        Flag for variable slits mode
    motors_controller : GeneralMotorsController
        Controller for general motors
    slits_position : list
        List of slits positions
    ni_pci_6221 : VoltageAcquisition
        Voltage acquisition instance
    baseline_scanning : Varian634BaselineScanning
        Baseline scanning instance
    path_baseline : str
        Path for baseline data storage
    chemical_kinetics : Varian634KineticsAnalysis
        Kinetics analysis instance
    path : str
        Path for experiment data storage
    date : str
        Date of the experiment
    slot_size : str
        Size of the experiment slot
    echantillon_name : str
        Name of the studied species
    title_file : str
        Title for the experiment file
    title_file_echantillon : str
        Title for the experiment file with species name
    csv : CSVTransformer
        CSV transformer instance
    noise_processing : PhotodiodeNoiseReducer
        Photodiode noise reducer instance
    peak_search_window : int
        Window size for peak search
    graph : Varian634ExperimentPlotter
        Experiment plotter instance
    """

    def __init__(self, arduino_motors_instance, arduino_sensors_instance):
        """
        Constructs all the necessary attributes for the SpectroVariableSlits object.

        Parameters
        ----------
        arduino_motors_instance : serial.Serial
            Instance of serial connection for motor control
        arduino_sensors_instance : pyfirmata.Arduino
            Instance of Arduino for sensor control
        """
        # init hardware
        self.arduino_motors = arduino_motors_instance
        self.arduino_sensors = arduino_sensors_instance
        self.mode_variable_slits = True
        self.motors_controller = GeneralMotorsController(self.arduino_motors, self.arduino_sensors)
        self.slits_position = [1, 2, 3, 4]
        self.ni_pci_6221 = VoltageAcquisition()
        # init experiment tools
        self.baseline_scanning = Varian634BaselineScanning(self.arduino_motors, self.arduino_sensors, self.mode_variable_slits)
        self.path_baseline = "./client/python/core/data_baseline"
        self.chemical_kinetics = Varian634KineticsAnalysis(self.arduino_motors, self.arduino_sensors, self.mode_variable_slits)
        self.path, self.date, self.slot_size = experim_manager.creation_directory_date_slot()
        self.echantillon_name = input("Nom de l'espèce étudié ? ")
        self.title_file = self.date + '_' + self.slot_size
        self.title_file_echantillon = self.date + '_' + self.slot_size + '_' + self.echantillon_name
        self.csv = CSVTransformer(self.path)
        # init digital processing
        self.noise_processing = PhotodiodeNoiseReducer()
        self.peak_search_window = 1
        self.graph = Varian634ExperimentPlotter(self.path, self.echantillon_name, self.peak_search_window)

    def slits_variable_scanning(self, screw_travel, number_measurements):
        """
        Program that scans all slits of the Varian during scanning mode.

        Parameters
        ----------
        screw_travel : int
            Screw travel for scanning
        number_measurements : int
            Number of measurements to be performed
        """
        self.motors_controller.initialisation_motors()
        for slits in self.slits_position:
            self.motors_controller.move_slits(slits)
            self.motors_controller.wait_for_idle()
            self.baseline_scanning.scanning_acquisition(screw_travel, number_measurements)

    def slits_variable_chemical_kinetics(self, time_acquisition, wavelengths, delay_between_measurements):
        """
        Program that scans all slits of the Varian during kinetic analysis mode.

        Parameters
        ----------
        time_acquisition : int
            Time of acquisition for each measurement
        wavelengths : list
            List of wavelengths to be analyzed
        delay_between_measurements : int
            Delay between consecutive measurements
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
    arduino_motors.write("\r\n\r\n".encode())  # encode to convert "\r\n\r\n"
    time.sleep(INITIALIZATION_TIME)   # Wait for initialization of GRBL
    arduino_motors.flushInput()  # Empty the input buffer by removing all its contents.

    # INITIALISATION Force optique:

    arduino_sensors = Arduino(COM_PORT_SENSORS)
    MODE_SLITS = False

    slits_mode = SpectroVariableSlits(arduino_motors, arduino_sensors)
    TIME_ACQUISITION = 2
    WAVELENGTHS = [400, 450, 500]
    DELAY = 1
    slits_mode.slits_variable_chemical_kinetics(TIME_ACQUISITION, WAVELENGTHS, DELAY)
