"""
This program will create the baseline for the absorbance analysis of the sample.
"""
import time

# Motors
from kinematic_chains.motors.all_motors import wait_for_motor_idle
from kinematic_chains.motors.screw_motor import (initialisation_motor_screw, move_screw, reset_screw_position)
from kinematic_chains.motors.mirror_cuves_motor import (move_mirror_cuves_motor, initialisation_mirror_cuves_motor)
# Specify individual imports from end_stop_sensor module
# Voltage acquisition
from electronics_controler.ni_pci_6221 import voltage_acquisition_baseline, get_solution_cuvette

# Data processing
from utils.data_csv import save_data_csv
from utils.draw_curve import graph
from utils.directory_creation import creation_directory_date_slot

from baseline import initialize_measurement, calculate_wavelength


def chemical_kinetics(arduino_motors, arduino_sensors, fente, temps_d_acquisition, longueurs_a_analyser):
    """
    This program will focus on 1 or 3 wavelengths within a user-defined time period and 
    introduce a delay between two absorbance measurements during the solution analysis

    """
    initialize_measurement(arduino_motors=arduino_motors, arduino_sensors=arduino_sensors, screw_translation_speed=10)

# End-of-file (EOF)


