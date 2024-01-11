"""
This program will create the baseline for the absorbance analysis of the sample.
"""
import time
import numpy as np

# Motors
from kinematic_chains.motors.motors_varian_634 import GeneralMotorsController


# Voltage acquisition
from electronics_controler.ni_pci_6221 import VoltageAcquisition

# Data processing
from utils.data_csv import save_data_csv
from utils.draw_curve import graph
from utils.directory_creation import creation_directory_date_slot, get_solution_cuvette

class SpectroBaseline:
    def __init__(self, arduino_motors, arduino_sensors):
        self.arduino_motors = arduino_motors
        self.arduino_sensors = arduino_sensors
        
    def initialize_measurement(self, screw_translation_speed):
        """
        Initializes the necessary components for the measurement.
        Input:
            arduino_motors (serial.Serial): Instance représentant l'Arduino connecté aux moteurs.
            arduino_sensors (pyfirmata.Arduino): Instance représentant l'Arduino connecté à la fourche
            screw_translation_speed (int): Translation speed of the screw

        Output:
            echantillon_name (string): Name of the sample that the user wants to analyze
            path (string): Working directory for the experiment
            date (string): Today's date
            slot_size (string): Size of the slot used
        """
        echantillon_name = input("Nom de l'espèce étudié ? ")
        [path, date, slot_size] = creation_directory_date_slot()
        initialisation_mirror_cuves_motor_v2(arduino_motors=self.arduino_motors, arduino_optical_fork=self.arduino_sensors)
        wait_for_motor_idle(arduino_motors=self.arduino_motors) 
        initialisation_motor_screw(arduino_motors=self.arduino_motors, arduino_end_stop=self.arduino_sensors, screw_translation_speed=screw_translation_speed)
        return echantillon_name, path, date, slot_size

    def perform_step_measurement_baseline(self, samples_per_channel, sample_rate, pulse_frequency, channels):
        """
        Effectue une mesure à un pas donné et retourne les tensions mesurées.
        """
        g_code = '$X' + '\n'
        self.arduino_motors.write(g_code.encode())

        voltage_photodiode_1 = voltage_acquisition_baseline(samples_per_channel=samples_per_channel, sample_rate=sample_rate, square_wave_frequency=pulse_frequency, channels=channels, channel='ai0')

        move_mirror_cuves_motor(self.arduino_motors, 0.33334)
        time.sleep(1)
        voltage_photodiode_2 = voltage_acquisition_baseline(samples_per_channel=samples_per_channel, sample_rate=sample_rate, square_wave_frequency=pulse_frequency, channels=channels, channel='ai1')

        move_mirror_cuves_motor(self.arduino_motors, -0.33334)
        time.sleep(1)

        return voltage_photodiode_1, voltage_photodiode_2

    def calculate_wavelength(self, position):
        """
        Calcule la longueur d'onde en fonction de la position.
        """
        return -31.10419907 * position + 800

    def precision_mode_baseline(self, screw_travel, number_measurements, screw_translation_speed, pulse_frequency, samples_per_channel, sample_rate, channels):
        """
        Exécute le mode de précision pour la mesure et retourne les résultats.
        """
        choice = get_solution_cuvette()
        voltages_photodiode_1, voltages_photodiode_2 = [], []
        no_screw, wavelength = [0], []
        step = screw_travel / number_measurements
        time_per_step = (step * 60) / screw_translation_speed

        for i in range(1, number_measurements):
            voltage_1, voltage_2 = self.perform_step_measurement_baseline(samples_per_channel, sample_rate, pulse_frequency, channels)
            voltages_photodiode_1.append(voltage_1)
            voltages_photodiode_2.append(voltage_2)
            position = i * step
            move_screw(arduino_motors=self.arduino_motors, screw_course=position, screw_translation_speed=screw_translation_speed)
            time.sleep(time_per_step)
            no_screw.append(position)
            wavelength.append(self.calculate_wavelength(position))

        reference_solution, sample_solution = (voltages_photodiode_1, voltages_photodiode_2) if choice == 'cuve 1' else (voltages_photodiode_2, voltages_photodiode_1)
        return list(reversed(wavelength)), list(reversed(reference_solution)), list(reversed(sample_solution)), list(reversed(no_screw))

    def baseline_acquisition(self, screw_travel, number_measurements, screw_translation_speed, pulse_frequency, samples_per_channel, sample_rate, channels):
        """
        Effectue une acquisition complète et sauvegarde les données.
        """
        [echantillon, path, date, slot_size] = self.initialize_measurement(screw_translation_speed)
        data_acquisition = self.precision_mode_baseline(screw_travel, number_measurements, screw_translation_speed, pulse_frequency, samples_per_channel, sample_rate, channels)
        title_data_acquisition = ["Longueur d'onde (nm)", "Tension référence (Volt)", "Tension échantillon (Volt)", "pas de vis (mm)"]
        title_file = 'baseline' + date + '_' + slot_size + '_' + echantillon
        save_data_csv(path=path, data_list=data_acquisition, title_list=title_data_acquisition, file_name=title_file)
        wait_for_motor_idle(self.arduino_motors)
        reset_screw_position(self.arduino_motors, screw_travel, screw_translation_speed)
        absorbance_baseline = np.log(data_acquisition[2]/data_acquisition[1])
        return title_file, absorbance_baseline
# End-of-file (EOF)

