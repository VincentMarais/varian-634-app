"""
This program will create the baseline for the absorbance analysis of the sample.
"""
import time

# Motors
from kinematic_chains.motors.all_motors import wait_for_motor_idle
from kinematic_chains.motors.screw_motor import (initialisation_motor_screw, move_screw, reset_screw_position)
from kinematic_chains.motors.mirror_cuves_motor import (move_mirror_cuves_motor, initialisation_mirror_cuves_motor_v2)
# Specify individual imports from end_stop_sensor module
# Voltage acquisition
from electronics_controler.ni_pci_6221 import voltage_acquisition_baseline, get_solution_cuvette

# Data processing
from utils.data_csv import save_data_csv
from utils.draw_curve import graph
from utils.directory_creation import creation_directory_date_slot

def initialize_measurement(arduino_motors, arduino_sensors, screw_translation_speed):
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
 
    # Initialization of cuvettes and motors
    echantillon_name = input("Name of the sample under study ? ")
    [path, date, slot_size] = creation_directory_date_slot()
    initialisation_mirror_cuves_motor_v2(arduino_motors=arduino_motors, arduino_optical_forkYaY=arduino_sensors)
    initialisation_motor_screw(arduino_motors=arduino_motors, arduino_end_stop=arduino_sensors, screw_translation_speed=screw_translation_speed)
    return echantillon_name, path, date, slot_size


def perform_step_measurement_baseline(arduino_motors, samples_per_channel, sample_rate, pulse_frequency, channels):

    """
    Effectue une mesure à un pas donné et retourne les tensions mesurées.
    """
    # Mesure pour la photodiode 1  samples_per_channel, sample_rate,
    voltage_photodiode_1 = voltage_acquisition_baseline(samples_per_channel=samples_per_channel, sample_rate=sample_rate, square_wave_frequency=pulse_frequency, channels=channels, channel='ai0')

    # Rotation du miroir et mesure pour la photodiode 2
    move_mirror_cuves_motor(arduino_motors, 0.33334)  # Rotation de 60°
    time.sleep(1)  # Délai pour stabilisation
    voltage_photodiode_2 = voltage_acquisition_baseline(samples_per_channel=samples_per_channel, sample_rate=sample_rate, square_wave_frequency=pulse_frequency, channels=channels, channel='ai1')

    # Retour du miroir à sa position initiale
    move_mirror_cuves_motor(arduino_motors, -0.33334)
    time.sleep(1)

    return voltage_photodiode_1, voltage_photodiode_2

def calculate_wavelength(position):
    """
    Calcule la longueur d'onde en fonction de la position.
    """
    # Formule spécifique au système (cf Rapport de projet 2022-2023 "Acquisition du signal")
    return -31.10419907 * position + 800

def precision_mode_baseline(arduino_motors, screw_travel, number_measurements, screw_translation_speed, pulse_frequency, samples_per_channel, sample_rate, channels):
    """
    Exécute le mode de précision pour la mesure et retourne les résultats.
    """
    choice = get_solution_cuvette()
    voltages_photodiode_1, voltages_photodiode_2 = [], []
    no_screw, wavelength = [0], []
    step = screw_travel / number_measurements
    time_per_step = (step * 60) / screw_translation_speed

    for i in range(1, number_measurements):
        position = i * step
        voltage_1, voltage_2 = perform_step_measurement_baseline(arduino_motors, samples_per_channel, sample_rate, pulse_frequency, channels)
        voltages_photodiode_1.append(voltage_1)
        voltages_photodiode_2.append(voltage_2)
        no_screw.append(position)
        wavelength.append(calculate_wavelength(position))
        move_screw(arduino_motors=arduino_motors, screw_course=position, screw_translation_speed=screw_translation_speed)
        time.sleep(time_per_step)
    reference_solution, sample_solution = (voltages_photodiode_1, voltages_photodiode_2) if choice == 'cuve 1' else (voltages_photodiode_2, voltages_photodiode_1)
    return list(reversed(wavelength)), list(reversed(reference_solution)), list(reversed(sample_solution)), list(reversed(no_screw))

def baseline_acquisition(arduino_motors, arduino_sensors, screw_travel, number_measurements, screw_translation_speed, pulse_frequency, samples_per_channel, sample_rate, channels):
    """
    Effectue une acquisition complète et sauvegarde les données.
    """
    [echantillon, path, date, slot_size] = initialize_measurement(arduino_motors, arduino_sensors, screw_translation_speed)
    data_acquisition = precision_mode_baseline(arduino_motors, screw_travel, number_measurements, screw_translation_speed, pulse_frequency, samples_per_channel, sample_rate, channels)
    title_data_acquisition=["Longueur d\'onde (nm)", "Tension référence (Volt)", "Tension échantillon (Volt)", "pas de vis (mm)"]
    tilte_file=date + '_' + slot_size + '_' + echantillon
    save_data_csv(path=path, data_list=data_acquisition, title_list=title_data_acquisition, file_name=tilte_file)
    # Gestion des états du moteur
    wait_for_motor_idle(arduino_motors)
    reset_screw_position(arduino_motors, screw_travel, screw_translation_speed)
    #graph(path=path)
# End-of-file (EOF)


