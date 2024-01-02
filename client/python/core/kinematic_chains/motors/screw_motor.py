"""
This program controls the motor that drives the screw which allows the 
rotation of the reflection diffraction grating of the VARIAN 634.
"""

import time
from pyfirmata import util, INPUT
from all_motors import wait_for_motor_idle


class ScrewController:
    """
    Class controls the motor that drives the screw which allows the 
    rotation of the reflection diffraction grating of the VARIAN 634.
    """
    def __init__(self, arduino_motors, arduino_end_stop):
        """
        Initialize the ScrewController class.

        Args:
            arduino_motors (serial.Serial): Motor Arduino instance connected to the screw.
            arduino_end_stop (Arduino): End stop sensor instance.
        """
        self.arduino_motors = arduino_motors
        self.arduino_end_stop = arduino_end_stop

    def set_screw_speed(self, speed):
        """
        Set the screw translation speed.
        
        Args:
            arduino_motors (serial.Serial): Motor Arduino instance connected to the screw.
            speed (int): Screw translation speed.
        """
        self.arduino_motors.write(f'$110={speed}\n'.encode())
        time.sleep(0.5)

    def move_screw(self, distance, speed, relative=False):
        """
        Move the screw that drives the diffraction grating.
        
        Args:
            arduino_motors (serial.Serial): Motor Arduino instance connected to the screw.
            distance (float): Screw position to move to.
            speed (int): Screw translation speed.
            relative (bool): True for relative movement, False for absolute.
        """
        self.set_screw_speed(speed)
        mode = 'G91\n' if relative else 'G90\n'
        self.arduino_motors.write(f'{mode}G0X{distance}\n'.encode())

    def end_stop_state(self, pin=2):
        """
        Get the state of the end stop sensors at the screw.
        
        Args:
            arduino_end_stop (Arduino): End stop sensor instance.
            pin (int): Digital pin number for the end stop sensor.
        
        Returns:
            bool: State of the end stop sensor.
        """
        self.arduino_end_stop.digital[pin].mode = INPUT
        util.Iterator(self.arduino_end_stop).start()
        time.sleep(1)
        return self.arduino_end_stop.digital[pin].read()

    def get_screw_position(self):
        """
        Get the current position of the screw.
        
        Args:
            arduino_motors (serial.Serial): Motor Arduino instance connected to the screw.
        
        Returns:
            str: Current screw position along the X-axis.
        """
        self.arduino_motors.write(b"?\n")
        return self.arduino_motors.readline().decode().strip().split(":")[1]

    def initialize_screw(self, pin=4):
        """
        Initialize the screw for the start of the experiment.
        
        Args:
            arduino_motors (serial.Serial): Motor Arduino instance connected to the screw.
            arduino_end_stop (Arduino): End stop sensor instance.
            pin (int): Digital pin number for the end stop sensor.
        """
        self.arduino_motors.write('G91\n'.encode())
        self.arduino_end_stop.digital[pin].mode = INPUT
        util.Iterator(self.arduino_end_stop).start()
        time.sleep(1)

        self.arduino_motors.write('$X\n$H\n'.encode())
        while self.arduino_end_stop.digital[pin].read():
            print("Waiting for motor to reach the start position...")
            time.sleep(0.1)

        print("Diffraction grating motor is ready for acquisition!")
        wait_for_motor_idle(arduino_motors=self.arduino_motors)

# Utilisation de la classe
# arduino_motors et arduino_end_stop doivent être définis au préalable
#screw_controller = ScrewController(arduino_motors, arduino_end_stop)
#screw_controller.initialize_screw()