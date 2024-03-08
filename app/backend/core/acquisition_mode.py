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

# Motors
from core.kinematic_chains.motors_varian_634 import GeneralMotorsController

# Voltage acquisition
from core.electronics_controler.ni_pci_6221 import VoltageAcquisition

# Data processing
from core.utils.experiment_manager import ExperimentManager
from core.utils.digital_signal_processing import PhotodiodeNoiseReducer


class Varian634AcquisitionMode:
    """
    Manages the operation modes for Varian 634 instruments including baseline, calibration, 
    scanning, and kinetics analysis. It controls motors for movement, acquires voltage 
    signals from sensors, and processes these signals to compute absorbance and other metrics.
    """

    def __init__(self, arduino_motors_instance, arduino_sensors_instance, sample_name, cuvette_choice):
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
        self.slits_position = [0, 0.07, 0.07, 0.08] # position of slits [2nm, 1nm, 0.5nm, 0.2nm]
        self.daq = VoltageAcquisition()
        self.channels = ['Dev1/ai0', 'Dev1/ai1']

        # Init digital processing
        self.signal_processing = PhotodiodeNoiseReducer()
        self.peak_search_window = 60
        # Init experiment tools
        self.experim_manager = ExperimentManager(sample_name)  
        self.raw_data = os.path.join(os.getcwd() ,'raw_data') 
        self.path, self.date, self.slot_size = self.experim_manager.creation_directory_date_slot(self.raw_data)
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
        step = (course_final - course_initial)/number_measurements
        print("step", step)
        print(number_measurements)
        self.motors_controller.execute_g_code("G91")
        self.motors_controller.move_screw(course_initial)
        time.sleep(course_initial/10)
        return step, number_measurements


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

   

    def precision_mode(self, step, number_measurements):
        """
        Performs precise measurements across a range of positions, calculates wavelength, and stores results.

        Parameters:
            screw_travel: Total distance for the screw to travel during the measurement.
            number_measurements: Number of measurements to take across the screw travel distance.

        Returns:
            A tuple containing lists of wavelengths, absorbance, reference voltages, sample voltages, and screw positions.
        """
        # Precision measurement setup
        voltages_reference, voltages_sample = [], []
    
        no_screw, wavelengths, absorbances = [], [], []
        time_per_step = (step * 60) / 10  # Time calculation for each step

        self.motors_controller.unlock_motors()
        self.motors_controller.execute_g_code("G91")  # Set relative movement mode
        time.sleep(1)  # Wait for command acknowledgment
        for i in range(0, number_measurements):
            voltages_photodiode_1, voltages_photodiode_2 = self.perform_step_measurement()
            # Move diffraction grating
            self.motors_controller.move_screw(step)
            [voltage_reference, voltage_sample] = self.experim_manager.link_cuvette_voltage(self.cuvette_choice, 
                                                                                voltages_photodiode_1, voltages_photodiode_2)
            # Store measurement data for plotting
            voltages_reference.append(voltage_reference)
            voltages_sample.append(voltage_sample)
            position = i * step
            no_screw.append(position + step)
            wavelengths.append(self.signal_processing.calculate_wavelength(position))
            
            absorbances.append(np.log10(voltage_sample/voltage_reference))
            # Save data incrementally             
            title_data_acquisition = ["Longueur d'onde (nm)", "Absorbance", "Tension rÃ©fÃ©rence (Volt)", "Tension Ã©chantillon (Volt)", 
                                  "pas de vis (mm)"]
            datas = [wavelengths, absorbances, voltage_reference, voltage_sample, no_screw]
            title_file = "raw_data_" + self.title_file_sample
            self.experim_manager.save_data_csv(self.path, datas, title_data_acquisition, title_file)            
            time.sleep(time_per_step)# Wait for diffraction grating adjustment
        
        # Calculate absorbance based on measurement choice         

        return wavelengths, absorbances, voltages_reference, voltages_sample, no_screw

    def acquisition(self, wavelenght_min, wavelenght_max, wavelenght_step, slot_size):
        """
        Manages the complete acquisition process, including motor initialization and data saving.

        Parameters:
            screw_travel: Total distance for the screw to travel.
            number_measurements: Total number of measurements to perform.
            mode: Acquisition mode (e.g., calibration, baseline, scanning).
            mode_variable_slits: Flag to use variable slit positions or not.

        Returns:
            The result of the precision mode operation, including wavelengths and absorbance values.
        """
        # state_motor_motor_slits 
        self.motors_controller.initialisation_motors(slot_size)
        
        [step , number_measurements] = self.initialisation_setting(wavelenght_min, wavelenght_max, wavelenght_step)
        
        data_acquisition = self.precision_mode(step, number_measurements)

        # Data saving
        title_data_acquisition = ["Longueur d'onde (nm)", "Absorbance", "Tension rÃ©fÃ©rence (Volt)", "Tension Ã©chantillon (Volt)", 
                                  "pas de vis (mm)"]
        title_file = "raw_data_" + self.title_file_sample
        self.experim_manager.save_data_csv(self.path, data_acquisition, title_data_acquisition, title_file)  
        self.motors_controller.wait_for_idle()
        self.motors_controller.reset_screw_position(step*number_measurements)   
           
        return data_acquisition[:2]
