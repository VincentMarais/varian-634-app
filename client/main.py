import os
import time
import tkinter as tk
import datetime

# MODES
from backend.core.baseline_scanning import Varian634BaselineScanning

# TOOLS
from frontend.real_time_graph import RealTimeGraphApp
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
    MODE_SLITS = False
    experim_manager = ExperimentManager()    
    current_date = datetime.datetime.now()
    current_day = current_date.strftime("%d_%m_%Y")        
    PHYSICAL_DATAS = ["Longueur d'onde (nm)", "Tension photodiode 1 (Volt)"]
    USER_PATH =  experim_manager.choose_folder()
    RAW_DATA_FILE = os.path.join(os.getcwd() ,'raw_data\\raw_data' + current_day + '.csv' ) 
    print(RAW_DATA_FILE)
    baseline_scanning = Varian634BaselineScanning(arduino_motors, arduino_sensors, USER_PATH, MODE_SLITS)
    ROOT = tk.Tk()
    real_time_graph = RealTimeGraphApp(ROOT, RAW_DATA_FILE, PHYSICAL_DATAS)
    baseline_scanning.scanning_acquisition(26, 400)
    ROOT.mainloop()

    