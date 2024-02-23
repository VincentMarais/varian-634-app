import time
import tkinter as tk

# MODES
from backend.core.acquisition_mode import Varian634AcquisitionMode

# TOOLS
from backend.core.utils.experiment_manager import ExperimentManager


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
    SAMPLE_NAME = "Bromophénol" 
    experim_manager = ExperimentManager(SAMPLE_NAME)
     
    ROOT = tk.Tk()
    USER_PATH =  experim_manager.choose_folder(ROOT) 
    
    baseline_scanning = Varian634AcquisitionMode(arduino_motors, arduino_sensors, USER_PATH, SAMPLE_NAME)
    baseline_scanning.baseline_verification()
    #baseline_scanning.scanning_acquisition(780, 790, 10)
    ROOT.mainloop()

    
