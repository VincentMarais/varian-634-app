"""
This program controls all the motors present on the VARIAN 634.
"""

import time
import re
from pyfirmata import util, INPUT, Arduino

class GeneralMotorsController:
    """
    This class represents a controller for all the motors on the VARIAN 634.

    Attributes:
        arduino_motors (object): An instance of the Arduino motor to control.
        arduino_sensors (object): An instance of the Arduino sensors.

        screw_motor (list): Motor parameters for the screw motor [axis, g_code_speed, speed, gcode_type].
        pin_limit_switch_screw (list): Digital pins for the limit switch next to the mechanical stop at the screw.

        mirror_cuves_motor (list): Motor parameters for the mirror cuves motor [axis, g_code_speed, speed, gcode_type].
        pin_limit_switch_mirror_cuves (list): Digital pins for the limit switch for the mirror cuves.

        slits_motor (list): Motor parameters for the slits motor [axis, g_code_speed, speed, gcode_type].
        pin_limit_switch_slits (list): Digital pins for the limit switch for the slits.
    """
    def __init__(self, arduino_motors_instance, arduino_sensors_instance):
        """
        Initialize the controller with an Arduino motor and sensors instance.

        Args:
            arduino_motors_instance (object): An instance of the Arduino motor to control.
            arduino_sensors_instance (object): An instance of the Arduino sensors.
        """
        # Arduino
        self.arduino_motors = arduino_motors_instance
        self.arduino_sensors = arduino_sensors_instance

        # Screw motor
        self.screw_motor = ['X', '$110', 10, 'G91/n']  # [axis, g_code_speed, speed, gcode_type]
        self.pin_limit_switch_screw = [2, 4]

        # Mirror cuves motor
        self.mirror_cuves_motor = ['Y', '$111', 14, 'G91/n']
        self.pin_limit_switch_mirror_cuves = [3]

        # Slits motor
        self.slits_motor = ['Z', '$112', 10, 'G91/n']
        self.pin_limit_switch_slits = [5]

    def set_motors_speed(self, motor_parameters, speed):
        """
        Set the motor translation speed.

        Args:
            motor_parameters (list): Motor parameters [axis, speed, movement type].
            speed (int): Motor translation speed.
        """
        g_code = motor_parameters[1] + str(speed) + '\n'
        self.execute_g_code(g_code)
        time.sleep(0.5)

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

        # Read and process the response
        response = str(self.arduino_motors.readline())
        print("Raw Response:", response)
        while 'MPos' not in response:
            response = str(self.arduino_motors.readline())

        # Extract X, Y, and Z coordinates
        match = re.search(r"MPos:([-+]?[0-9]*\.?[0-9]+),([-+]?[0-9]*\.?[0-9]+),([-+]?[0-9]*\.?[0-9]+)", response)
        x_pos, y_pos, z_pos = [float(coordinate) for coordinate in match.groups()]
        return x_pos, y_pos, z_pos

    def execute_g_code(self, g_code):
        """
        Send a G-code command to the motor.

        Args:
            g_code (str): The G-code command to be sent to the motor.
        """
        self.arduino_motors.write(g_code.encode())

    def move_motor(self, motor_parameters, distance):
        """
        Move the motor by a specified distance.

        Args:
            motor_parameters (list): Motor parameters [axis, speed, movement type].
            distance (float): Distance to move.
        """
        mode = motor_parameters[3]
        gcode = mode + "G0" + motor_parameters[0] + str(distance) + '\n'
        self.execute_g_code(gcode)

    def move_mirror_motor(self, distance):
        """
        Move the mirror motor by a specified distance.

        Args:
            distance (float): Distance to move.
        """
        self.move_motor(self.mirror_cuves_motor, distance)

    def move_screw(self, distance):
        """
        Move the screw motor by a specified distance.

        Args:
            distance (float): Distance to move.
        """
        self.move_motor(self.screw_motor, distance)

    def move_slits(self, distance):
        """
        Move the slits motor by a specified distance.
        """
        self.move_motor(self.slits_motor, distance)

    def reset_screw_position(self, screw_course):
        """
        Move the screw motor backward.

        Args:
            screw_course (float): Position of the screw to move backward.
        """
        self.move_screw(distance=-screw_course)

    def initialize_end_stop(self, pin_list):
        """
        Initialize the end stop sensors at the screw.

        Args:
            pin_list (list): Digital pins for the end stop sensors.
        """
        for pin in pin_list:
            self.arduino_sensors.digital[pin].mode = INPUT

        # Create an Iterator instance to not miss incoming data
        it = util.Iterator(self.arduino_sensors)
        it.start()

        # Allow the iterator to start
        time.sleep(1)

    def initialize_mirror_position(self, pin_mirror):
        """
        An alternative method to initialize the mirror position based on a specific requirement.

        Args:
            pin_mirror (list): Digital pin for the mirror position.
        """
        pin = pin_mirror[0]
        self.initialize_end_stop(self.pin_limit_switch_mirror_cuves)
        self.move_motor(self.mirror_cuves_motor, 1)
        state = self.arduino_sensors.digital[pin].read()
        while state is True:
            print("Cuve 1 not reached because ", state)
            state = self.arduino_sensors.digital[pin].read()
        pos_y = self.get_position_xyz()[1]
        self.move_mirror_motor(distance=pos_y)
        print(pos_y)

    def initialisation_motor_screw_slipt(self):
        """
        Initialize the screw motor for the start of the experiment.
        """
        all_pin = self.pin_limit_switch_screw
        self.initialize_end_stop(all_pin)
        digital_value = self.arduino_sensors.digital[all_pin[0]].read()
        g_code = '$X' + '\n'
        self.arduino_motors.write(g_code.encode())
        g_code = '$H' + '\n'
        self.arduino_motors.write(g_code.encode())
        while digital_value is True:
            digital_value = self.arduino_sensors.digital[all_pin[0]].read()
            print("The motor is not at the start: ", digital_value)
            time.sleep(0.1)
        print("Diffraction network motor is ready for acquisition!")
        print("We are back to the start!")
        self.wait_for_idle()
        print("Diffraction network motor is ready for acquisition!")
        # End-of-file (EOF)

    def initialisation_motors(self):
        """
        Initializes all motors to start an acquisition.
        """
        pin_mirror = self.pin_limit_switch_mirror_cuves
        self.initialize_mirror_position(pin_mirror)
        self.wait_for_idle()
        self.initialisation_motor_screw_slipt()

if __name__ == "__main__":
    import serial

    # MOTOR INITIALIZATION:

    COM_PORT_MOTORS = 'COM3'
    COM_PORT_SENSORS = 'COM9'
    BAUD_RATE = 115200
    INITIALIZATION_TIME = 2

    arduino_motors = serial.Serial(COM_PORT_MOTORS, BAUD_RATE)
    arduino_motors.write("\r\n\r\n".encode())  # encode to convert "\r\n\r\n"
    time.sleep(INITIALIZATION_TIME)   # Wait for GRBL initialization
    arduino_motors.flushInput()  # Flush the input buffer, removing all its contents.

    # OPTICAL FORK INITIALIZATION:

    arduino_sensors = Arduino(COM_PORT_SENSORS)

    motors_controller = GeneralMotorsController(arduino_motors, arduino_sensors)

    # Test set_motors_speed function
    motors_controller.set_motors_speed(motors_controller.screw_motor, 10)  # Set screw motor speed to 10

    # Test get_motor_state function
    motor_state = motors_controller.get_motor_state()
    print("Motor State:", motor_state)

    # Test display_grbl_parameter function
    motors_controller.display_grbl_parameter()

    # Test get_position_xyz function
    current_position = motors_controller.get_position_xyz()
    print("Current Position:", current_position)

    # Test execute_g_code function
    motors_controller.execute_g_code("G0 X1 Y1 Z0.01")  # Example G-code command

    # Test wait_for_idle function
    motors_controller.wait_for_idle()

    # Test move_motor function
    motors_controller.move_motor(motors_controller.screw_motor, 1)  # Move screw motor by 5 units

    # Test stop_motors function
    motors_controller.stop_motors()

    # Test resume_cycle function
    motors_controller.resume_cycle()

    # Test wait_for_idle function
    motors_controller.wait_for_idle()

    # Test move_mirror_motor function
    motors_controller.move_mirror_motor(2)  # Move mirror motor by 2 units

    # Test move_screw function
    motors_controller.move_screw(1)  # Move screw motor by 3 units

    # Test initialisation_motors function
    motors_controller.initialisation_motors()
