"""
This program controls all the motors present on the VARIAN 634.
"""
import time
import re

class GeneralMotorsController:
    """
    This program controls all the motors present on the VARIAN 634.
    """
    def __init__(self, arduino_motors):
        """
        Initialize the controller with an Arduino motor instance.

        Args:
            arduino_motors (object): An instance of the Arduino motor to control.
        """
        self.arduino_motors = arduino_motors

    def get_motor_state(self):
        """
        Query and return the current state of the motor.

        Returns:
            str: The current state of the motor (based on the motor's response).
        """
        self.execute_g_code('?')
        return self.arduino_motors.read(20)  # Read the first 20 characters for state

    def display_grbl_parameter(self):
        """
        Display the GRBL parameters of the motor.
        """
        self.execute_g_code('$G')
        print(self.arduino_motors.read(75))

    def stop_motors(self):
        """
        Immediately stop the motor.
        """
        self.execute_g_code('!')

    def resume_cycle(self):
        """
        Resume motor operation after a stop command.
        """
        self.execute_g_code('~')

    def wait_for_idle(self):
        """
        Block execution until the motor is idle.
        """
        while 'Idle' not in str(self.get_motor_state()):
            pass

    def get_position_xyz(self):
        """
        Get and return the current XYZ position of the motor.

        Returns:
            list: A list [X, Y, Z] containing the current coordinates of the motor.
        """
        self.execute_g_code('?')
        time.sleep(0.1)
        response = self.arduino_motors.readline().decode()
        match = re.search(r"MPos:([-+]?[0-9]*\.?[0-9]+),([-+]?[0-9]*\.?[0-9]+),([-+]?[0-9]*\.?[0-9]+)", response)
        return [float(coordinate) for coordinate in match.groups()]

    def execute_g_code(self, g_code):
        """
        Send a G-code command to the motor.

        Args:
            g_code (str): The G-code command to be sent to the motor.
        """
        self.arduino_motors.write(f'{g_code}\n'.encode())

# End-of-file (EOF)
