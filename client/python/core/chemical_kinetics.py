"""
"This program will perform an analysis 
of the absorbance kinetics for the absorbance 
analysis of the sample."""

import time
import numpy as np

# Motors
from kinematic_chains.motors.all_motors import GeneralMotorsController
from kinematic_chains.motors.screw_motor import ScrewController
from kinematic_chains.motors.mirror_cuves_motor import MirrorCuvesController

# Voltage acquisition
from electronics_controler.ni_pci_6221 import VoltageAcquisition

from utils.data_csv import save_data_csv

from baseline import SpectroBaseline

class SpectroKineticsAnalysis:
    """
    Ce programme se concentrera sur 1 ou 3 longueurs d'onde 
    dans une période définie par l'utilisateur et introduira un délai entre deux mesures 
    d'absorbance lors de l'analyse de la solution.
    """
    def __init__(self, arduino_motors, arduino_sensors):
        self.arduino_motors = arduino_motors
        self.arduino_sensors = arduino_sensors

    def wait_for_user_confirmation(self, prompt):
        while input(prompt) != 'Oui':
            pass

    def measure_voltage(self, channel, samples_per_channel, sample_rate, square_wave_frequency, channels):
        return voltage_acquisition_scanning(samples_per_channel, sample_rate, square_wave_frequency, channels, channel=channel)

    def run_analysis(self, temps_d_acquisition, longueurs_a_analyser, samples_per_channel, sample_rate, square_wave_frequency, channels, delay_between_measurements):
        [echantillon, path, date, slot_size] = SpectroBaseline.initialize_measurement(self.arduino_motors, self.arduino_sensors, screw_translation_speed=10)

        for longueur_d_onde in longueurs_a_analyser:
            course_vis = 1 / 31.10419907 * (800 - longueur_d_onde)
            move_screw(self.arduino_motors, course_vis, screw_translation_speed=12)
            wait_for_motor_idle(self.arduino_motors)

            choice = get_solution_cuvette()
            wait_for_motor_idle(self.arduino_motors)

            cuvette_prompt = "Avez-vous mis votre solution dans la cuve appropriée ? "
            self.wait_for_user_confirmation(cuvette_prompt)

            tension_blanc = self.measure_voltage("ai0" if choice == "cuve 1" else "ai1", samples_per_channel, sample_rate, square_wave_frequency, channels)
            move_mirror_cuves_motor(self.arduino_motors, 0.33334)

            start_time = time.time()
            tensions_echantillon = []
            temps = []

            while time.time() - start_time < temps_d_acquisition:
                tension_echantillon_t = self.measure_voltage("ai1" if choice == "cuve 1" else "ai0", samples_per_channel, sample_rate, square_wave_frequency, channels)
                tensions_echantillon.append(tension_echantillon_t)
                temps.append(time.time() - start_time)
                time.sleep(delay_between_measurements)

            move_mirror_cuves_motor(self.arduino_motors, 0.33334)

            absorbance = np.log(np.array(tensions_echantillon) / tension_blanc)
            data_acquisition = [longueur_d_onde, temps, absorbance]
            title_file = f'{date}_{slot_size}_{echantillon}_longueur_{longueur_d_onde}'
            save_data_csv(path, data_acquisition, ["Longueur d'onde (nm)", "Temps (s)", "Absorbance"], title_file)

            reset_screw_position(self.arduino_motors, course_vis, screw_translation_speed=10)

# Usage
# analyzer = ChemicalKineticsAnalyzer(arduino_motors, arduino_sensors)
# analyzer.run_analysis(temps_d_acquisition, longueurs_a_analyser, samples_per_channel, sample_rate, square_wave_frequency, channels, delay_between_measurements)
