"""
This program will scan wavelengths within a specific interval to detect the peak of absorbance in the solution.


Define deferente speed of analysis 3 for exampl (look the exampl in the spectro use in TP GP3A) :
- suvey 100nm/min
- half 10nm/min
- slow 1nm/min
"""
import time
from baseline import initialize_measurement, calculate_wavelength, baseline_acquisition
from electronics_controler.ni_pci_6221 import voltage_acquisition_scanning, get_solution_cuvette

# kinematic_chains
from kinematic_chains.motors.mirror_cuves_motor import (move_mirror_cuves_motor)
from kinematic_chains.motors.screw_motor import (move_screw, reset_screw_position)
from kinematic_chains.motors.all_motors import wait_for_motor_idle


# Data processing
from utils.data_csv import save_data_csv
from utils.draw_curve import graph
from utils.directory_creation import creation_directory_date_slot






def perform_step_measurement_scanning(arduino_motors, samples_per_channel, sample_rate, pulse_frequency, duty_cycle, channels):

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
    # Mesure pour la photodiode 1  samples_per_channel, sample_rate,
    voltage_photodiode_1 = voltage_acquisition_scanning(samples_per_channel=samples_per_channel, sample_rate=sample_rate, square_wave_frequency=pulse_frequency, duty_cycle=duty_cycle, channels=channels, channel='ai0')

    # Rotation du miroir et mesure pour la photodiode 2
    move_mirror_cuves_motor(arduino_motors, 0.33334)  # Rotation de 60°
    time.sleep(1)  # Délai pour stabilisation
    voltage_photodiode_2 = voltage_acquisition_scanning(samples_per_channel=samples_per_channel, sample_rate=sample_rate, square_wave_frequency=pulse_frequency, duty_cycle=duty_cycle, channels=channels, channel='ai1')

    # Retour du miroir à sa position initiale
    move_mirror_cuves_motor(arduino_motors, -0.33334)
    time.sleep(1)

    return voltage_photodiode_1, voltage_photodiode_2

def precision_mode_scanning(arduino_motors, screw_travel, number_measurements, screw_translation_speed, pulse_frequency, duty_cycle, samples_per_channel, sample_rate, channels):
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
        voltage_1, voltage_2 = perform_step_measurement_scanning(arduino_motors, samples_per_channel, sample_rate, pulse_frequency, duty_cycle, channels)
        voltages_photodiode_1.append(voltage_1)
        voltages_photodiode_2.append(voltage_2)
        no_screw.append(position)
        wavelength.append(calculate_wavelength(position))
        move_screw(arduino_motors=arduino_motors, screw_course=position, screw_translation_speed=screw_translation_speed)
        time.sleep(time_per_step)
    reference_solution, sample_solution = (voltages_photodiode_1, voltages_photodiode_2) if choice == 'cuve 1' else (voltages_photodiode_2, voltages_photodiode_1)
    return list(reversed(wavelength)), list(reversed(reference_solution)), list(reversed(sample_solution)), list(reversed(no_screw))

def scanning_acquisition(arduino_motors, arduino_sensors, screw_travel, number_measurements, screw_translation_speed, pulse_frequency, duty_cycle, samples_per_channel, sample_rate, channels):
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
    base_line_choise=input("Avez réalisé la ligne de base ?")
    while base_line_choise not in ['Oui', 'Non'] :
        base_line_choise=input("Avez réalisé la ligne de base ?")
    if base_line_choise == 'Oui' :
        pass
    else:
        baseline_acquisition(arduino_motors, arduino_sensors, screw_travel, number_measurements, screw_translation_speed, pulse_frequency, samples_per_channel, sample_rate, channels)
    
    [echantillon, path, date, slot_size] = initialize_measurement(arduino_motors, arduino_sensors, screw_translation_speed)
    data_acquisition = precision_mode_scanning(arduino_motors, screw_travel, number_measurements, screw_translation_speed, pulse_frequency, duty_cycle, samples_per_channel, sample_rate, channels)
    absorbance=
    title_data_acquisition=["Longueur d\'onde (nm)", "Tension référence (Volt)", "Tension échantillon (Volt)", "pas de vis (mm)"]
    tilte_file=date + '_' + slot_size + '_' + echantillon
    save_data_csv(path=path, data_list=data_acquisition, title_list=title_data_acquisition, file_name=tilte_file)
    # Gestion des états du moteur
    wait_for_motor_idle(arduino_motors)
    reset_screw_position(arduino_motors, screw_travel, screw_translation_speed)
    #graph(path=path)
# End-of-file (EOF)


