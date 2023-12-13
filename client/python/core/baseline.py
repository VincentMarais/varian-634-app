"""
This program will create the baseline for the absorbance analysis of the sample.
"""
import time

# Motors
from kinematic_chains.motors.all_motors import wait_for_motor_idle
from kinematic_chains.motors.screw_motor import (initialisation_motor_screw, move_screw, reset_screw_position)
from kinematic_chains.motors.mirror_cuves_motor import (move_mirror_cuves_motor, initialisation_mirror_cuves_motor)
# Specify individual imports from end_stop_sensor module
# from core.kinematic_chains.end_stop_sensor import specific_function

# Voltage acquisition
from electronics_controler.ni_pci_6221 import voltage_acquisition_baseline, get_solution_cuvette

# Data processing
from utils.data_csv import save_data_csv
from utils.draw_curve import graph

def initialize_measurement(arduino_motors, arduino_optical_fork, screw_translation_speed):
    """
    Initialise les composants nécessaires pour la mesure.
    """
    # Initialisation cuves et moteurs
    choice = get_solution_cuvette()
    initialisation_mirror_cuves_motor(arduino_motors, arduino_optical_fork)
    initialisation_motor_screw(arduino_motors, screw_translation_speed)
    return choice


def perform_step_measurement(arduino_motors, samples_per_channel, sample_rate, pulse_frequency, duty_cycle, channels):
    """
    Effectue une mesure à un pas donné et retourne les tensions mesurées.
    """
    # Mesure pour la photodiode 1
    voltage_photodiode_1 = voltage_acquisition_baseline(samples_per_channel, sample_rate, pulse_frequency, duty_cycle, channels, channel='ai0')

    # Rotation du miroir et mesure pour la photodiode 2
    move_mirror_cuves_motor(arduino_motors, 0.33334)  # Rotation de 60°
    time.sleep(0.5)  # Délai pour stabilisation
    voltage_photodiode_2 = voltage_acquisition_baseline(samples_per_channel, sample_rate, pulse_frequency, duty_cycle, channels, channel='ai1')

    # Retour du miroir à sa position initiale
    move_mirror_cuves_motor(arduino_motors, -0.33334) 
    time.sleep(0.5)

    return voltage_photodiode_1, voltage_photodiode_2

def calculate_wavelength(position):
    """
    Calcule la longueur d'onde en fonction de la position.
    """
    # Formule spécifique au système (cf Rapport de projet 2022-2023 "Acquisition du signal")
    return -31.10419907 * position + 800

def precision_mode(arduino_motors, arduino_optical_fork, screw_travel, number_measurements, screw_translation_speed, pulse_frequency, duty_cycle, samples_per_channel, sample_rate, channels):
    """
    Exécute le mode de précision pour la mesure et retourne les résultats.
    """
    choice = initialize_measurement(arduino_motors, arduino_optical_fork, screw_translation_speed)
    voltages_photodiode_1, voltages_photodiode_2 = [], []
    no_screw, wavelength = [], []
    step = screw_travel / number_measurements
    time_per_step = (step * 60) / screw_translation_speed

    for i in range(number_measurements):
        position = i * step
        voltage_1, voltage_2 = perform_step_measurement(arduino_motors, position, samples_per_channel, sample_rate, pulse_frequency, duty_cycle, channels)
        voltages_photodiode_1.append(voltage_1)
        voltages_photodiode_2.append(voltage_2)
        no_screw.append(position)
        wavelength.append(calculate_wavelength(position))
        move_screw(arduino_motors=arduino_motors, screw_course=step, screw_translation_speed=screw_translation_speed)
        time.sleep(time_per_step)

    reference_solution, sample_solution = (voltages_photodiode_1, voltages_photodiode_2) if choice == 'cuve 1' else (voltages_photodiode_2, voltages_photodiode_1)
    return list(reversed(wavelength)), list(reversed(reference_solution)), list(reversed(sample_solution)), list(reversed(no_screw))

def acquisition(arduino_motors, screw_travel, number_measurements, screw_translation_speed, file_reference_solution, sample_solution_file, sample_solution_name, title, repertory):
    """
    Effectue une acquisition complète et sauvegarde les données.
    """
    [wavelength, voltages_reference_solution, voltages_sample_solution, no_screw] = precision_mode(arduino_motors, screw_travel, number_measurements, screw_translation_speed)

    #save_data_csv(path=repertory, 'Longueur d\'onde (nm)', 'Tension échantillon (Volt)', 'Liste_pas_vis')
    #save_data_csv(file_reference_solution, wavelength, voltages_reference_solution, no_screw, 'Longueur d\'onde (nm)', 'Tension blanc (Volt)', 'Liste_pas_vis')

    # Gestion des états du moteur
    wait_for_motor_idle(arduino_motors)
    reset_screw_position(arduino_motors, screw_travel, screw_translation_speed)
    #graph(file_reference_solution, sample_solution_file, sample_solution_name, title, repertory)
