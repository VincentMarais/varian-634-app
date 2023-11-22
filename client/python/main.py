"""
This module controls a Varian 634 spectrometer setup, including initialization
of an Arduino board and a NI-PCI 6221 card. It manages data acquisition and
processing for spectrometry analysis.
"""

import time
import serial
import numpy as np
from pyfirmata import Arduino, util

# Adjust the following imports according to your project structure
from core.dual_beam import acquition
from core.utils.directory_creation import creation_directory_date_slot
from core.electronics_controler.optical_fork import optical_fork_state
# INITIALISATION OF FILE FOR THE PROGRAM
[REPERTORY, DATE, SLOT_SIZE] = creation_directory_date_slot()

# INITIALIZATION OF NI-PCI 6221 CARD
PULSE_FREQUENCY = np.array([20.0])  # 20Hz, maximum voltage amplitude at the photodiode terminals
DUTY_CYCLE = np.array([0.5])  # Optimal duty cycle for measurement
SAMPLES_PER_CHANNEL = 30000  # Number of samples to retrieve
SAMPLE_RATE = 250000  # Maximum sampling frequency of the card
CHANNELS = ['Dev1/ai0', 'Dev1/ai1']

# INITIALIZATION OF ARDUINO FOR OPTICAL FORK
arduino_optical_fork = serial.Serial('COM6', 9600)  # Remplacez 'COM3' par le port série correspondant à votre Arduino

"""
# INITIALIZATION OF ARDUINO FOR MOTORS
COM_PORT = 'COM3'
BAUD_RATE = 115200
INITIALIZATION_TIME = 2
S = serial.Serial(COM_PORT, BAUD_RATE)
S.write("\r\n\r\n".encode())
time.sleep(INITIALIZATION_TIME)
S.flushInput()
"""
# PROGRAM LAUNCH PARAMETERS
SCREW_TRAVEL = 2  # 7mm
NUMBER_MEASUREMENTS = 10
SCREW_TRANSLATION_SPEED = 10  # mm/min
"""
sample_name = input("Sample name: ")

reference_solution_file = f'{REPERTORY}\\Tension_blanc_{DATE}_{SLOT_SIZE}.csv'
sample_solution_file = f'{REPERTORY}\\Tension_echantillon_{DATE}_{SLOT_SIZE}.csv'

title = f"Absorbance_{sample_name}_{DATE}_{SLOT_SIZE}"

acquition(S, SCREW_TRAVEL, NUMBER_MEASUREMENTS, SCREW_TRANSLATION_SPEED, reference_solution_file, sample_solution_file, sample_name, title, REPERTORY)

"""

optical_fork_state(arduino_optical_fork)
