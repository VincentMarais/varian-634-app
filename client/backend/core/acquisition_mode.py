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

Pour une acquisition longue désactiver la mise en veille du PC


"""
import time
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import serial

# Motors
from backend.core.kinematic_chains.motors_varian_634 import GeneralMotorsController

# Voltage acquisition
from backend.core.electronics_controler.ni_pci_6221 import VoltageAcquisition

# Data processing
from backend.core.utils.experiment_manager import ExperimentManager
from backend.core.utils.digital_signal_processing import PhotodiodeNoiseReducer


class Varian634AcquisitionMode:
    """
    Manages the operation modes for Varian 634 instruments including baseline, calibration, 
    scanning, and kinetics analysis. It controls motors for movement, acquires voltage 
    signals from sensors, and processes these signals to compute absorbance and other metrics.
    """

    def __init__(self, arduino_motors_instance, arduino_sensors_instance, path_user, sample_name):
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
        self.path_user = path_user      
        self.path, self.date, self.slot_size = self.experim_manager.creation_directory_date_slot(self.path_user)
        self.raw_data = os.path.join(os.getcwd() ,'raw_data') 
        self.sample_name = sample_name
        self.choice = self.experim_manager.get_solution_cuvette()
        self.title_file_sample = self.date + '_' + self.slot_size + '_' + self.sample_name
        

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
        voltages_photodiode_1, voltages_photodiode_2 = [], []
        no_screw, wavelength = [], []
        time_per_step = (step * 60) / 10  # Time calculation for each step

        self.motors_controller.unlock_motors()
        self.motors_controller.execute_g_code("G91")  # Set relative movement mode
        time.sleep(1)  # Wait for command acknowledgment

        for i in range(0, number_measurements):
            voltage_1, voltage_2 = self.perform_step_measurement()
            # Move diffraction grating
            self.motors_controller.move_screw(step)
            # Store measurement data for plotting
            voltages_photodiode_1.append(voltage_1)
            voltages_photodiode_2.append(voltage_2)
            position = i * step
            no_screw.append(position + step)
            wavelength.append(self.signal_processing.calculate_wavelength(position))
            # Save data incrementally             
            title_data_acquisition = ["Longueur d'onde (nm)", "Tension photodiode 1 (Volt)", "Tension photodiode 2 (Volt)", 
                                  "pas de vis (mm)"]
            datas = [wavelength, voltages_photodiode_1, voltages_photodiode_2, no_screw]
            title_file = "raw_data_" + self.date
            self.experim_manager.save_data_csv(self.raw_data, datas, title_data_acquisition, title_file)            
            time.sleep(time_per_step)# Wait for diffraction grating adjustment
        
        # Calculate absorbance based on measurement choice
            

        return wavelength, voltages_photodiode_1, voltages_photodiode_2, no_screw

    def acquisition(self, wavelenght_min, wavelenght_max, wavelenght_step, mode, slot_size, mode_variable_slits):
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
        if mode_variable_slits:
            self.motors_controller.initialisation_motors(slot_size, mode_variable_slits)
        else:
            self.motors_controller.initialisation_motors(self.slot_size, mode_variable_slits)
        
        [step , number_measurements] = self.initialisation_setting(wavelenght_min, wavelenght_max, wavelenght_step)
        data_acquisition = self.precision_mode(step, number_measurements)

        # Data saving
        title_data_acquisition = ["Longueur d'onde (nm)", "Absorbance", "Tension photodiode 1 (Volt)", "Tension photodiode 2 (Volt)", 
                                  "pas de vis (mm)"]
        title_file = mode + "_" + self.date
        self.experim_manager.save_data_csv(self.raw_data, data_acquisition, title_data_acquisition, title_file)
        self.motors_controller.wait_for_idle()
        self.motors_controller.reset_screw_position(step*number_measurements)

        # Calibration plot
        if mode == 'calibration':
            plt.figure()            
            plt.plot(data_acquisition[4], data_acquisition[2], '-', color='blue', label = "Tension photodiode 1 (Volt)")
            plt.plot(data_acquisition[4], data_acquisition[3], '-', color='red', label= "Tension photodiode 2 (Volt)")
            plt.grid(True)
            plt.legend()
            plt.xlabel("pas de vis (mm)")
            plt.ylabel("Tension (Volt)")
            plt.title("Spectre de la lampe au Xénon")
            plt.savefig(self.path + '\\' + title_file + ".pdf")
    
        return data_acquisition

    def initialisation_setting(self, wavelenght_min, wavelenght_max, wavelength_step):
        course_lambda_min = self.signal_processing.calculate_course(wavelenght_min)
        course_lambda_max = self.signal_processing.calculate_course(wavelenght_max)
        step = self.signal_processing.calculate_course(wavelength_step)
        print("final_course : " , course_lambda_min)
        print("initialiale_course", course_lambda_max)
        print("step", step)
        step = self.signal_processing.calculate_course(wavelength_step)
        screw_travel = course_lambda_min - course_lambda_max 
        print("step", screw_travel)
        number_measurements = int(screw_travel/step)
        print(number_measurements)
        return step, number_measurements

    def acquisition_baseline(self, wavelenght_min, wavelenght_max, wavelenght_step, slot_size, mode_variable_slits):
        """
        Conducts a baseline acquisition to establish a reference point for future measurements.

        Parameters:
            screw_travel: Total screw travel distance to cover during the baseline acquisition.
            number_measurements: Number of measurements to take across the screw travel distance.
            mode_variable_slits: Flag indicating whether to adjust slit positions during the acquisition.

        Returns:
            The result of the complete acquisition process, specific to the baseline mode.
        """
        [screw_travel, number_measurements] = self.initialisation_setting(wavelenght_min, wavelenght_max, wavelenght_step)
        if mode_variable_slits:
            return self.acquisition(screw_travel, number_measurements, 'baseline', slot_size, mode_variable_slits)
        else:
            return self.acquisition(screw_travel, number_measurements, 'baseline')

    def acquisition_calibration(self, screw_travel=26, number_measurements=600, mode_variable_slits=False):
        """
        Performs a full calibration acquisition to calibrate the diffraction grating for accurate measurements.
        (find the relation betwen wavelength and no screw)

        Parameters:
            screw_travel (int): Preset total distance for the calibration screw to travel.
            number_measurements (int): Preset total number of measurements for the calibration process.
            mode_variable_slits: Flag to adjust slit positions during calibration; not used in this context.

        Returns:
            None; results are directly managed by the acquisition method.
        """
        self.acquisition(screw_travel, number_measurements, 'calibration', mode_variable_slits)
        

    def baseline_verification(self):
        """
        Verifies the existence of a baseline file and decides on creating a new one if necessary.

        Checks for the presence of a baseline file named according to the date of the experiment.
        If absent, prompts the user to initiate baseline acquisition. If present, offers the choice
        to proceed with the existing baseline or create a new one.

        Returns:
            Absorbance values from the chosen or newly created baseline file.
        """

        self.experim_manager.create_directory(self.raw_data)
        baseline_file = os.path.join(self.raw_data, 'baseline_' + self.date)
        print(baseline_file)
        # Verification if the baseline_date_heure.csv file exists
        if not os.path.exists(baseline_file + ".csv"):
            print('Le fichier : ' + baseline_file + ".csv" + '  n\'est pas créé.')
            self.experim_manager.delete_files_in_directory(self.raw_data)
            print("Réalisation de la baseline")
            absorbance_baseline = self.acquisition_baseline(780,795,5, "Fente_1nm", True)[1]

        else:
            reponse = input("Souhaitez-vous réaliser une nouvelle baseline, 'Oui' ou 'Non'? ").lower()

            if reponse == 'oui':
                absorbance_baseline = self.acquisition_baseline(780,795,5, "Fente_1nm", True)[1]
                print("Exécution de acquisition_baseline")
                return absorbance_baseline
                
            elif reponse == 'non':
                file_baseline= 'baseline_' + self.date
                print(file_baseline)
                baseline_file = f"{self.raw_data}\\{file_baseline}.csv"
                data_baseline = pd.read_csv(baseline_file, encoding='ISO-8859-1')
                absorbance_baseline = data_baseline['Absorbance']

            else:
                while reponse not in ['oui', 'non']:
                    reponse = input("Répondez par 'Oui' ou 'Non'. Souhaitez-vous réaliser une nouvelle baseline ? ").lower()
    

    def scanning_acquisition(self, lambda_min, lambda_max, wavelength_step):
        """
        Conducts a scanning acquisition over a specified wavelength range and step size.

        Parameters:
            lambda_min (int): Minimum wavelength for the scanning range.
            lambda_max (int): Maximum wavelength for the scanning range.
            step (int): Step size for wavelength adjustment during the scan.
            mode_variable_slits: Flag indicating whether to adjust slit positions during scanning.

        Initiates by verifying baseline, calculating screw travel based on wavelength range, and
        performing the acquisition with specified parameters.
        """
        # Réalisation de la baseline pour une acquisition correct
        self.baseline_verification()
        # On réinitialise les moteurs pour une meilleure 
        self.motors_controller.initialisation_motors()
        course_lambda_min = self.signal_processing.calculate_course(lambda_min)
        course_lambda_max = self.signal_processing.calculate_course(lambda_max)
        step = self.signal_processing.calculate_course(wavelength_step)
        print("final_course : " , course_lambda_min)
        print("initialiale_course", course_lambda_max)
        print("step", step)
        step = self.signal_processing.calculate_course(wavelength_step)
        screw_travel = course_lambda_min - course_lambda_max 
        print("step", screw_travel)
        number_measurements = int(screw_travel/step)
        print(number_measurements)

        self.arduino_motors.flushInput()
        self.motors_controller.execute_g_code("G91")
        self.motors_controller.move_screw(course_lambda_max)
        cuvette_prompt = "Avez-vous mis votre solution dans la cuve appropriée ? "
        self.experim_manager.wait_for_user_confirmation(cuvette_prompt)
        self.motors_controller.wait_for_idle()

        data_acquisition = self.precision_mode(step, number_measurements)
        wavelength = data_acquisition[0]
        voltages_photodiode_1 = data_acquisition[1]
        voltages_photodiode_2 = self.signal_processing.correction_baseline(data_acquisition[1], data_acquisition[2])
        [reference_solution, sample_solution] = self.experim_manager.link_cuvette_voltage(self.choice, 
                                                                                voltages_photodiode_1, voltages_photodiode_2)

        absorbance = np.log10(np.array(reference_solution)/np.array(sample_solution))
        title_data_acquisition = ["Longueur d'onde (nm)", "Absorbance"]
        data_acquisition = [wavelength, absorbance]
        title_file = self.title_file_sample + '_mode_scanning'
        self.experim_manager.save_data_csv(self.path, data_acquisition, title_data_acquisition, title_file)
        self.experim_manager.save_display(self.path, title_file, 'Longueur d\'onde (nm)', "Absorbance", title_file)
        # End-of-file (EOF)


# Analysis of the absorbance kinetics for the absorbance analysis of the sample.
    def run_kinetics_analysis(self, time_acquisition, delay_between_measurements, wavelengths, mode_variable_slits):
        """
        Executes kinetics analysis over specified wavelengths with time intervals.

        Parameters:
            time_acquisition: Total time to conduct the kinetics measurement.
            delay_between_measurements: Time delay between consecutive measurements.
            wavelengths: List of wavelengths to perform the kinetics analysis at.
            mode_variable_slits: Flag indicating whether to adjust slit positions during kinetics analysis.

        Performs kinetics measurements by adjusting to specified wavelengths and measuring
        absorbance over time, allowing for analysis of chemical reactions or sample changes.
        """
        absorbance_baseline = self.baseline_verification()

        if mode_variable_slits:
            pass
        else:
            self.motors_controller.initialisation_motors()
        # Trie de la liste dans l'ordre décroissant
        # Afin que le moteur s'initialise plus vite
       
        wavelengths.sort(reverse=True)
        print(wavelengths)
        course_vis = 1 / 31.10419907 * (800 - wavelengths[0])
        # Deplace
        self.motors_controller.execute_g_code("G90")
        self.motors_controller.move_screw(course_vis)
        self.motors_controller.wait_for_idle()
        cuvette_prompt = "Avez-vous mis votre solution dans la cuve appropriée ? "

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

            absorbance_kinetics = np.log10(voltage_ref/voltages_sample)
            absorbance = self.signal_processing.sample_absorbance(absorbance_baseline, absorbance_kinetics)
            data_acquisition = [wavelength, moment, absorbance]
            file_name = f'{self.date}_{self.slot_size}_{self.sample_name}_longueur_{wavelength}'
            title_file = ["Longueur d'onde (nm)", "Temps (s)", "Absorbance"]
            self.experim_manager.save_data_csv(self.path, data_acquisition, title_file, file_name)
            self.experim_manager.save_display(self.path, title_file, "Temps (s)", 'Absorbance', file_name)
            self.motors_controller.reset_screw_position(course_vis)
            self.motors_controller.wait_for_idle()
        

    def slits_variable_scanning(self, lambda_min, lambda_max, step):
        """
        Executes scanning across all slit positions for a given wavelength range and step size.

        Parameters:
            lambda_min (int): Minimum wavelength for the scanning range.
            lambda_max (int): Maximum wavelength for the scanning range.
            step (int): Step size for wavelength adjustment during the scan.

        Iterates through predefined slit positions, conducting scanning acquisitions at each position,
        to analyze the effect of slit width on measurement results.
        """
        self.motors_controller.initialisation_motors()
        for slits in self.slits_position:
            self.motors_controller.move_slits(slits)
            self.motors_controller.wait_for_idle()
            self.scanning_acquisition(lambda_min, lambda_max, step, True)

    def slits_variable_chemical_kinetics(self, time_acquisition, wavelengths, delay_between_measurements):
        """
        Conducts chemical kinetics analysis across all slit positions for specified wavelengths.

        Parameters:
            time_acquisition: Total time for the kinetics measurement.
            wavelengths: List of wavelengths to perform kinetics analysis at.
            delay_between_measurements: Time delay between consecutive measurements.

        Similar to the slits_variable_scanning method, but focused on kinetics analysis,
        this method iterates through slit positions, adjusting the system for measurements
        that reveal how slit width affects kinetics measurements.
        """
        self.motors_controller.initialisation_motors()
        for slits in self.slits_position:
            self.motors_controller.move_slits(slits)
            self.motors_controller.wait_for_idle()
            self.run_kinetics_analysis(time_acquisition, delay_between_measurements, wavelengths, True)
