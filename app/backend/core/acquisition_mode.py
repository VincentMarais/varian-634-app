"""
This program manages the operation modes for Varian 634 instruments including baseline, calibration, 
scanning, and kinetics analysis.


Define deferente speed of analysis 3 for exampl (look the exampl in the spectro use in TP GP3A) :
- suvey 100nm/min
- half 10nm/min
- slow 1nm/min  

Visible range with the screw pitch:
400nm -> 5.4mm and ending at 800 nm -> 18.73nm

Course maxi : 26mm

Pour une acquisition longue dÃ©sactiver la mise en veille du PC


"""
import time
import os
import numpy as np
import serial
from pyfirmata import Arduino
from flask_socketio import SocketIO

# Motors
from core.kinematic_chains.motors_varian_634 import GeneralMotorsController

# Voltage acquisition
from core.electronics_controler.ni_pci_6221 import ElectronicVarian634

# Data processing
from core.utils.experiment_manager import ExperimentManager
from core.utils.digital_signal_processing import SignalProcessingVarian634


class Varian634AcquisitionMode:
    """
    Manages the operation modes for Varian 634 instruments including baseline, calibration, 
    scanning, and kinetics analysis. It controls motors for movement, acquires voltage 
    signals from sensors, and processes these signals to compute absorbance and other metrics.
    """

    def __init__(self, arduino_motors_instance: serial.Serial, arduino_sensors_instance: Arduino, 
                 socketio : SocketIO, sample_name : str, cuvette_choice : str, slot_size : str):
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
        self.motors_controller = GeneralMotorsController(self.arduino_motors, self.arduino_sensors)
        self.slits_position = [0, 0.065, 0.135, 0.22] # position of slits [2nm, 1nm, 0.5nm, 0.2nm]
        self.daq = ElectronicVarian634()
        self.channels = ['Dev1/ai0', 'Dev1/ai1']

        # Init digital processing
        self.signal_processing = SignalProcessingVarian634()
        self.peak_search_window = 60
        self.slot_size = slot_size
        # Init experiment tools
        self.socketio = socketio
        self.experim_manager = ExperimentManager(sample_name, slot_size)  
        self.raw_data = os.path.join(os.getcwd() ,'raw_data') 
        self.path, self.date = self.experim_manager.creation_directory_date_slot(self.raw_data)
        self.sample_name = sample_name
        self.cuvette_choice = cuvette_choice
        self.title_file_sample = f"{self.date}_{self.slot_size}_{self.sample_name}"
        

    def initialisation_setting(self, wavelenght_min, wavelenght_max, wavelength_step):
        """
        Initi
        """

        course_final = self.signal_processing.calculate_course(wavelenght_min)
        course_initial = self.signal_processing.calculate_course(wavelenght_max)
        print("final_course : " , course_final)
        print("initialiale_course", course_initial)
        number_measurements = int( (wavelenght_max - wavelenght_min)/wavelength_step )
        print("number_measurements", number_measurements)
        step = (course_final - course_initial)/number_measurements
        print("step", step)
        print(number_measurements)
        self.motors_controller.unlock_motors()
        self.motors_controller.relative_move()
        time.sleep(1)
        self.motors_controller.move_screw(course_initial)
        time.sleep(course_initial*60/10)
        return course_initial, step, number_measurements


    def perform_step_measurement(self):
        """
        Measures voltage across two photodiodes by switching mirror position between measurements.

        Returns:
            Tuple containing measured voltages from photodiode 1 and photodiode 2.
        """
        voltage_photodiode_2 = self.daq.voltage_acquisition_scanning_baseline(self.channels[0])
        self.motors_controller.move_mirror_motor(0.33334)  # Move mirror to switch cuvette
        time.sleep(1)  # Wait for mirror adjustment
        voltage_photodiode_1 = self.daq.voltage_acquisition_scanning_baseline(self.channels[1])
        self.motors_controller.move_mirror_motor(-0.33334)  # Move mirror back
        time.sleep(1)

        return voltage_photodiode_1, voltage_photodiode_2

   

    def precision_mode(self, course_initial, step, number_measurements):
        """
        Performs precise measurements across a range of positions, calculates wavelength, and stores results.

        Parameters:
            screw_travel: Total distance for the screw to travel during the measurement.
            number_measurements: Number of measurements to take across the screw travel distance.

        Returns:
            A tuple containing lists of wavelengths, absorbance, reference voltages, sample voltages, and screw positions.
        """
        # Precision measurement setup
        voltages_reference, voltages_sample = np.array([]), np.array([])
    
        no_screw, wavelengths, absorbances = np.array([]), np.array([]), np.array([])
        time_per_step = (step * 60) / 10  # Time calculation for each step

        self.motors_controller.unlock_motors()
        self.motors_controller.execute_g_code("G91")  # Set relative movement mode
        time.sleep(1)  # Wait for command acknowledgment
        for i in range(0, number_measurements + 1):
            voltages_photodiode_1, voltages_photodiode_2 = self.perform_step_measurement()
            # Move diffraction grating
            [voltage_reference, voltage_sample] = self.experim_manager.link_cuvette_voltage(self.cuvette_choice, 
                                                                                voltages_photodiode_1, voltages_photodiode_2)
            # Store measurement data for plotting
            voltages_reference = np.append(voltages_reference, voltage_reference)
            voltages_sample= np.append(voltages_sample, voltage_sample)

            print("voltages_reference :", voltages_reference, "type", voltages_reference.dtype)
            print("voltages_sample :", voltages_sample, "type", voltages_sample.dtype)
            position = course_initial + i * step
            no_screw = np.append(no_screw, position)
            print("no_screw :", no_screw , "type", no_screw.dtype)
            wavelengths = np.append(wavelengths, self.signal_processing.calculate_wavelength(position))
            print("wavelengths :", wavelengths, "type", wavelengths.dtype)
            absorbances= np.append(absorbances, np.log10(voltage_reference/voltage_sample))
            print("absorbances :", absorbances, "type", absorbances.dtype)
            self.motors_controller.move_screw(step)

            # Save data incrementally             
            title_data_acquisition = ["Longueur d'onde (nm)", "Absorbance", "Tension reference (Volt)", "Tension echantillon (Volt)", 
                                  "pas de vis (mm)"]
            # .tolist() because all data was in numpy.float64 and that create conflict with 
            datas = [wavelengths, absorbances, voltages_reference, voltages_sample, no_screw]
            title_file = "raw_data_" + self.title_file_sample
            self.experim_manager.save_data_csv(self.path, datas, title_data_acquisition, title_file) 
            self.socketio.emit('update_data', {'data_y': np.log10(voltage_reference/voltage_sample), "data_x": self.signal_processing.calculate_wavelength(position), "slitId": self.slot_size})
           
            time.sleep(time_per_step)# Wait for diffraction grating adjustment         

        return wavelengths, absorbances, voltages_reference, voltages_sample, no_screw

    def acquisition(self, mode, wavelenght_min, wavelenght_max, wavelenght_step):
        """
        Manages the complete acquisition process, including motor initialization and data saving.

        Parameters:
            screw_travel: Total distance for the screw to travel.
            number_measurements: Total number of measurements to perform.
            mode: Acquisition mode (e.g., baseline, scanning).

        Returns:
            The result of the precision mode operation, including wavelengths and absorbance values.
        """
        # state_motor_motor_slits 
        self.motors_controller.initialisation_motors(self.slot_size)
        
        [course_initial, step , number_measurements] = self.initialisation_setting(wavelenght_min, wavelenght_max, wavelenght_step)
        data_acquisition = self.precision_mode(course_initial, step, number_measurements)
        # Data saving
        title_data_acquisition = ["Longueur d'onde (nm)", "Absorbance", "Tension reference (Volt)", "Tension echantillon (Volt)", 
                                  "pas de vis (mm)"]
        title_file = "raw_data_" + mode + "_" + self.title_file_sample
        self.experim_manager.save_data_csv(self.path, data_acquisition, title_data_acquisition, title_file)  
        self.motors_controller.wait_for_idle()
        self.motors_controller.reset_screw_position(step*number_measurements)   
        self.motors_controller.wait_for_idle()        
        return data_acquisition[:2]
