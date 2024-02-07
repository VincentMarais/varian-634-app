"""
This program will perform an analysis 
of the absorbance kinetics for the absorbance 
analysis of the sample.

"""
import os
import numpy as np

# Motors
from kinematic_chains.motors_varian_634 import GeneralMotorsController

# Voltage acquisition
from electronics_controler.ni_pci_6221 import VoltageAcquisition

# Data processing
from utils.draw_curve import Varian634ExperimentPlotter
from utils.experiment_manager import ExperimentManager
from utils.digital_signal_processing import PhotodiodeNoiseReducer



class Varian634KineticsAnalysis:
    """
    Ce programme se concentrera sur 1 ou 3 longueurs d'onde 
    dans une période définie par l'utilisateur et introduira un délai entre deux mesures 
    d'absorbance lors de l'analyse de la solution.
    """
    def __init__(self, arduino_motors_instance, arduino_sensors_instance, mode_variable_slits):
        """
        Constructs all the necessary attributes for the Varian634KineticsAnalysis object.

        Parameters
        ----------
            arduino_motors_instance : object
                instance of the Arduino motors
            arduino_sensors_instance : object
                instance of the Arduino sensors
            mode_variable_slits : bool
                mode variable slits
        """
        # init hardware
        self.arduino_motors = arduino_motors_instance
        self.arduino_sensors = arduino_sensors_instance
        self.mode_variable_slits = mode_variable_slits
        self.motors_controller = GeneralMotorsController(self.arduino_motors, self.arduino_sensors)
        self.daq = VoltageAcquisition()

        # init experiment tools
        self.experim_manager = ExperimentManager()  
        self.path_user = self.experim_manager.choose_folder()      
        self.path, self.date, self.slot_size = self.experim_manager.creation_directory_date_slot(self.path_user)
        self.raw_data = os.path.join(os.getcwd() ,'raw_data') 
        self.sample_name = input("Nom de l'espèce étudié ? ")
        self.choice = self.experim_manager.get_solution_cuvette()
        self.title_file_sample = self.date + '_' + self.slot_size + '_' + self.sample_name + '_' + self.slot_size

        # init digital processing
        self.noise_processing = PhotodiodeNoiseReducer()
        self.peak_search_window = 1
        self.graph = Varian634ExperimentPlotter(self.path, self.sample_name, self.peak_search_window)

    def run_kinetics_analysis(self, time_acquisition, wavelengths, delay_between_measurements):
        """
        Runs the kinetics analysis.

        Parameters
        ----------
        time_acquisition : int
            acquisition time
        wavelengths : list
            list of wavelengths
        delay_between_measurements : int
            delay between measurements

        Returns
        -------
        None
        """
        if self.mode_variable_slits:
            pass
        else:
            self.motors_controller.initialisation_motors()

        for wavelength in wavelengths:
            course_vis = 1 / 31.10419907 * (800 - wavelength)
            self.motors_controller.move_screw(course_vis)
            self.motors_controller.wait_for_idle()
            cuvette_prompt = "Avez-vous mis votre solution dans la cuve appropriée ? "
            self.experim_manager.wait_for_user_confirmation(cuvette_prompt)
            channel = "Dev1/ai0" if self.choice == "cuvette 1" else "Dev1/ai1"
            voltage_ref = self.daq.voltage_acquisition_scanning_baseline(channel)
            self.motors_controller.move_mirror_motor(0.33334)

            [moment, voltages_sample] = self.daq.voltage_acquisition_chemical_kinetics(channel, time_acquisition, delay_between_measurements)

            self.motors_controller.move_mirror_motor(-0.33334)

            absorbance = np.log10(voltage_ref/voltages_sample)
            data_acquisition = [wavelength, moment, absorbance]
            file_name = f'{self.date}_{self.slot_size}_{self.sample_name}_longueur_{wavelength}'
            title_file = ["Longueur d'onde (nm)", "Temps (s)", "Absorbance"]
            self.experim_manager.save_data_csv(self.path, data_acquisition, title_file, file_name)
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
    arduino_motors.write("\r\n\r\n".encode())  # encode pour convertir "\r\n\r\n" 
    time.sleep(INITIALIZATION_TIME)   # Attend initialisation un GRBL
    arduino_motors.flushInput()  # Vider le tampon d'entrée, en supprimant tout son contenu.

    # INITIALISATION Forche optique:
    arduino_sensors = Arduino(COM_PORT_SENSORS)
    MODE_SLITS = False

    kinetics_mode = Varian634KineticsAnalysis(arduino_motors, arduino_sensors, MODE_SLITS)
    TIME_ACQUISITION = 2
    WAVELENGTHS = [400, 450, 500]
    DELAY = 1
    kinetics_mode.run_kinetics_analysis(TIME_ACQUISITION, WAVELENGTHS, DELAY)
