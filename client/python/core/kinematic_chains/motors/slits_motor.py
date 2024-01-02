"""
This program will control the motors that manage 
the variable slits system of the VARIAN 634
"""

import time
from pyfirmata import INPUT


class VarianSlitsController:
    """
    class : control the motors that manage 
    the variable slits system of the VARIAN 634
    """
    def __init__(self, arduino_motors, arduino_end_stop):
        """
        Initialize the controller with motor and end-stop instances.
        
        Args:
            arduino_motors (object): Instance representing the motor controller (Arduino).
            arduino_end_stop (object): Instance representing the end-stop sensor (Arduino).
        """
        self.arduino_motors = arduino_motors
        self.arduino_end_stop = arduino_end_stop
        self.initialize_end_stop()
        self.initialize_motor()

    def initialize_motor(self):
        """
        Set the motor to absolute movement mode.
        """
        self.execute_g_code('G90\n')

    def initialize_end_stop(self):
        """
        Set up the end-stop sensor as an input device.
        """
        self.arduino_end_stop.digital[4].mode = INPUT
        time.sleep(1)

    def execute_g_code(self, g_code):
        """
        Send a G-code command to the motor.
        
        Args:
            g_code (str): The G-code command to be sent to the motor.
        """
        self.arduino_motors.write(f'{g_code}\n'.encode())

    def move_slits(self, distance, relative=False):
        """
        Move the slits by a specified distance. Set 'relative' to True for relative movement.
        
        Args:
            distance (float): The distance to move the slits by.
            relative (bool, optional): If True, the movement is relative; if False, it's absolute.
        """
        mode = 'G91' if relative else 'G90'
        self.execute_g_code(f'{mode}\nG0Z{distance}')

    def check_end_stop(self):
        """
        Continuously move the slits until the end-stop sensor is triggered.
        """
        while not self.arduino_end_stop.digital[4].read():
            self.move_slits(0.2, relative=True)

        self.execute_g_code('!')  # Stop the motor

    def get_slit_position(self):
        """
        Query and return the current position of the slits.
        
        Returns:
            str: The current position of the slits as a string.
        """
        self.arduino_motors.write(b"?z\n")
        response = self.arduino_motors.readline().decode().strip()
        position_z = response.split(":")[1]
        return position_z
# End-of-file (EOF)