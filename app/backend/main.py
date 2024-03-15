# MODES
from core.acquisition_mode import Varian634AcquisitionMode



if __name__ == "__main__":
    import serial
    from pyfirmata import Arduino

    # INITIALIZATION MOTOR:

    COM_PORT_MOTORS = 'COM3'
    COM_PORT_SENSORS = 'COM9'
    BAUD_RATE = 115200
    INITIALIZATION_TIME = 2

    arduino_motors = serial.Serial(COM_PORT_MOTORS, BAUD_RATE)

    # INITIALIZATION Optical Fork:

    arduino_sensors = Arduino(COM_PORT_SENSORS)
    SAMPLE_NAME = "Bromophenol" 
     
    
    baseline_scanning = Varian634AcquisitionMode(arduino_motors, arduino_sensors, SAMPLE_NAME, "cuvette 2", "Fente_2nm")
    baseline_scanning.acquisition(560, 630, 1)

    #baseline_scanning.initialisation_setting(480, 660, 1)

    