"""
This program will scan wavelengths within a specific interval to detect the peak of absorbance in the solution.


Define deferente speed of analysis 3 for exampl (look the exampl in the spectro use in TP GP3A) :
- suvey 100nm/min
- half 10nm/min
- slow 1nm/min
"""
import time
import numpy as np
import pandas as pd

from baseline import SpectroBaseline

# Motors
from kinematic_chains.motors.all_motors import GeneralMotorsController
from kinematic_chains.motors.screw_motor import ScrewController
from kinematic_chains.motors.mirror_cuves_motor import MirrorCuvesController

# Voltage acquisition
from electronics_controler.ni_pci_6221 import VoltageAcquisition

from utils.data_csv import save_data_csv

# Data processing
from utils.data_csv import save_data_csv
from utils.draw_curve import graph
from utils.directory_creation import creation_directory_date_slot
from utils.digital_signal_processing.interpolation import sample_absorbance



class SpectroScanningAnalysis:
    def __init__(self, arduino_motors, arduino_sensors, channels):
        self.arduino_motors = arduino_motors
        self.arduino_sensors = arduino_sensors
        self.channels = channels

    def perform_step_measurement_scanning(self, samples_per_channel, sample_rate, pulse_frequency, duty_cycle):
        """
    Effectue une mesure à un pas donné et retourne les tensions mesurées sur deux canaux.

    Args:
        arduino_motors (serial.Serial): Interface de communication avec les moteurs Arduino.
        samples_per_channel (int): Nombre d'échantillons par canal à mesurer.
        sample_rate (int): Fréquence d'échantillonnage des mesures.
        pulse_frequency (float): Fréquence de la forme d'onde carrée pour la stimulation.
        duty_cycle (float): Rapport cyclique de la forme d'onde carrée.
        channels (list): Liste des canaux utilisés pour la mesure.
    Returns:
        tuple: Tensions mesurées sur les photodiodes 1 et 2.
    """
        voltage_photodiode_1 = voltage_acquisition_scanning(samples_per_channel=samples_per_channel, sample_rate=sample_rate, square_wave_frequency=pulse_frequency, duty_cycle=duty_cycle, channels=self.channels, channel='ai0')

        move_mirror_cuves_motor(self.arduino_motors, 0.33334)  # 60° rotation
        time.sleep(1)  # Stabilization delay
        voltage_photodiode_2 = voltage_acquisition_scanning(samples_per_channel=samples_per_channel, sample_rate=sample_rate, square_wave_frequency=pulse_frequency, duty_cycle=duty_cycle, channels=self.channels, channel='ai1')

        move_mirror_cuves_motor(self.arduino_motors, -0.33334)
        time.sleep(1)

        return voltage_photodiode_1, voltage_photodiode_2

    @staticmethod
    def validate_user_input(prompt, valid_responses):
        response = input(prompt)
        while response not in valid_responses:
            response = input(prompt)
        return response

    def precision_mode_scanning(self, screw_travel, number_measurements, screw_translation_speed, pulse_frequency, duty_cycle, samples_per_channel, sample_rate):
        """
        Exécute le mode de précision pour les mesures en déplaçant la vis de mesure et retourne les résultats.

        Args:
            arduino_motors (serial.Serial): Interface de communication avec les moteurs Arduino.
            screw_travel (float): Distance totale que la vis doit parcourir.
            number_measurements (int): Nombre total de mesures à effectuer.
            screw_translation_speed (int): Vitesse de déplacement de la vis.
            pulse_frequency (float): Fréquence de la forme d'onde carrée pour la stimulation.
            duty_cycle (float): Rapport cyclique de la forme d'onde carrée.
            samples_per_channel (int): Nombre d'échantillons par canal à mesurer.
            sample_rate (int): Fréquence d'échantillonnage des mesures.
            channels (list): Liste des canaux utilisés pour la mesure.
        Returns:
        tuple: Données des longueurs d'onde, tensions de référence et échantillon, et positions de la vis.
        """
        choice = get_solution_cuvette()
        voltages_photodiode_1, voltages_photodiode_2 = [], []
        no_screw, wavelength = [0], []
        step = screw_travel / number_measurements
        time_per_step = (step * 60) / screw_translation_speed

        for i in range(1, number_measurements):
            position = i * step
            voltage_1, voltage_2 = self.perform_step_measurement_scanning(samples_per_channel, sample_rate, pulse_frequency, duty_cycle)
            voltages_photodiode_1.append(voltage_1)
            voltages_photodiode_2.append(voltage_2)
            no_screw.append(position)
            wavelength.append(SpectroBaseline.initialize_measurement(position))
            move_screw(self.arduino_motors, position, screw_translation_speed)
            time.sleep(time_per_step)
        reference_solution, sample_solution = (voltages_photodiode_1, voltages_photodiode_2) if choice == 'cuve 1' else (voltages_photodiode_2, voltages_photodiode_1)
        return list(reversed(wavelength)), list(reversed(reference_solution)), list(reversed(sample_solution)), list(reversed(no_screw))

    def scanning_acquisition(self, screw_travel, number_measurements, screw_translation_speed, pulse_frequency, duty_cycle, samples_per_channel, sample_rate):
        """
        Effectue une acquisition complète de données, sauvegarde les résultats et gère les états du moteur.

        Args:
            arduino_motors (serial.Serial): Interface de communication avec les moteurs Arduino.
            arduino_sensors (serial.Serial): Interface de communication avec les capteurs Arduino.
            screw_travel (float): Distance totale que la vis doit parcourir.
            number_measurements (int): Nombre total de mesures à effectuer.
            screw_translation_speed (int): Vitesse de déplacement de la vis.
            pulse_frequency (float): Fréquence de la forme d'onde carrée pour la stimulation.
            duty_cycle (float): Rapport cyclique de la forme d'onde carrée.
            samples_per_channel (int): Nombre d'échantillons par canal à mesurer.
            sample_rate (int): Fréquence d'échantillonnage des mesures.
            channels (list): Liste des canaux utilisés pour la mesure.
        """
        
        [echantillon, path, date, slot_size] = SpectroBaseline.initialize_measurement(self.arduino_motors, self.arduino_sensors, screw_translation_speed)
        
        base_line_choice = self.validate_user_input("Avez-vous réalisé la ligne de base ? (Oui/Non) ", ["Oui", "Non"])
        
        if base_line_choice == 'Oui':
            title_file_baseline = 'baseline' + date + '_' + slot_size + '_' + echantillon
            file_name_baseline = path + '/' + title_file_baseline + '.csv'
            data_baseline = pd.read_csv(file_name_baseline, encoding='ISO-8859-1')
            absorbance_baseline = data_baseline['Absorbance']
        else:
            [title_file, absorbance_baseline] = SpectroBaseline.baseline_acquisition(self.arduino_motors, self.arduino_sensors, screw_travel, number_measurements, screw_translation_speed, pulse_frequency, samples_per_channel, sample_rate, self.channels)

        data_acquisition = self.precision_mode_scanning(screw_travel, number_measurements, screw_translation_speed, pulse_frequency, duty_cycle, samples_per_channel, sample_rate)
        absorbance_scanning = np.log(np.divide(data_acquisition[2], data_acquisition[1]))
        absorbance = sample_absorbance(absorbance_baseline, absorbance_scanning, title_file)

        title_data_acquisition = ["Longueur d'onde (nm)", "Absorbance", "pas de vis (mm)"]
        data_acquisition = [data_acquisition[0], absorbance, data_acquisition[3]]
        title_file = date + '_' + slot_size + '_' + echantillon
        save_data_csv(path, data_acquisition, title_data_acquisition, title_file)

        wait_for_motor_idle(self.arduino_motors)
        reset_screw_position(self.arduino_motors, screw_travel, screw_translation_speed)
        # graph(path) # Uncomment if graph function is needed

# Example usage
# arduino_motors = ...  # Initialize arduino_motors
# arduino_sensors = ...  # Initialize arduino_sensors
# channels = ...  # Define channels
# spectro_analysis = SpectroAnalysis(arduino_motors, arduino_sensors, channels)
# spectro_analysis.scanning_acquisition(...)


