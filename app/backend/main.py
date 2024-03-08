import time
import tkinter as tk

# MODES
from core.acquisition_mode import Varian634AcquisitionMode

# TOOLS
from core.utils.experiment_manager import ExperimentManager


if __name__ == "__main__":
    import serial
    from pyfirmata import Arduino

    # INITIALIZATION MOTOR:

    COM_PORT_MOTORS = 'COM3'
    COM_PORT_SENSORS = 'COM9'
    BAUD_RATE = 115200
    INITIALIZATION_TIME = 2

    arduino_motors = serial.Serial(COM_PORT_MOTORS, BAUD_RATE)
    arduino_motors.write("\r\n\r\n".encode())  # encode to convert "\r\n\r\n"
    time.sleep(INITIALIZATION_TIME)  # Wait for initialization of GRBL
    arduino_motors.flushInput()  # Clear the input buffer by discarding its current contents.

    # INITIALIZATION Optical Fork:

    arduino_sensors = Arduino(COM_PORT_SENSORS)
    SAMPLE_NAME = "Bromophenol" 
    experim_manager = ExperimentManager(SAMPLE_NAME)
     
    USER_PATH =  "C:\\Users\\vimarais\\Documents\\Analyse"
    
    baseline_scanning = Varian634AcquisitionMode(arduino_motors, arduino_sensors, SAMPLE_NAME, "cuvette 1")
    baseline_scanning.acquisition(780, 790, 10, "Fente_1nm")

    