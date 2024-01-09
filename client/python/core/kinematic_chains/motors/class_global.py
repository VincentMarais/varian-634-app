"""
This program controls all the motors present on the VARIAN 634.
"""
import time
import re

class GeneralMotorsController:
    """
    This program controls all the motors present on the VARIAN 634.
    """
    def __init__(self, arduino_motors, arduino_sensor):
        """
        Initialize the controller with an Arduino motor instance.

        Args:
            arduino_motors (object): An instance of the Arduino motor to control.
        """
        self.arduino_motors = arduino_motors
        self.arduino_sensor=arduino_sensor
        self.screw_motor= [arduino_motors,'X', 10, False]
        self.mirror_cuves_motor=self.move_motor(axe='Y')
        self.slits_motor=self.move_motor(axe='Z')


    def move_motor(self, axe, distance, speed=10, relative=False):
        self.set_screw_speed(speed)
        mode = 'G91\n' if relative else 'G90\n'
        self.arduino_motors.write(f'{mode}G0{axe}{distance}\n'.encode())
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
        self.execute_g_code("?" + '\n')
        time.sleep(0.1)

        # Lire et traiter la réponse
        response = str(self.arduino_motors.readline())
        print("Réponse brute :", response)
        while 'MPos' not in response:
            response = str(self.arduino_motors.readline())    
        # Extraire les coordonnées X, Y, et Z
        match = re.search(r"MPos:([-+]?[0-9]*\.?[0-9]+),([-+]?[0-9]*\.?[0-9]+),([-+]?[0-9]*\.?[0-9]+)", response)        
        x_pos, y_pos, z_pos = [float(coordinate) for coordinate in match.groups()]
        return x_pos, y_pos, z_pos

    def execute_g_code(self, g_code):
        """
        Send a G-code command to the motor.

        Args:
            g_code (str): The G-code command to be sent to the motor.
        """
        self.arduino_motors.write(f'{g_code}\n'.encode())