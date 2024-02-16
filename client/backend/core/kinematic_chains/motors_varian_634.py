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
        # all digital pins used on the Arduino UNO 
        # with no CNC shield 
        self.all_pin = [2, 3, 4, 5]
        # Screw motor
        self.screw_motor = ['X', '$110', 10]  # [axis, g_code_speed, speed]
        # pin = 2 (between limits)
        self.pin_limit_switch_screw = [2, 4]

        # Slits motor
        self.slits_motor = ['Y', '$111', 14]  # [axis, g_code_speed, speed]
        # pin = 5 in optical fork between slits variable
        self.pin_limit_switch_slits = [5]
        self.slits_position = [0, 0.07, 0.14, 0.22] # position of slits [2nm, 1nm, 0.5nm, 0.2nm]
        self.name_slits = ["Fente_2nm", "Fente_1nm", "Fente_0_5nm", "Fente_0_2nm"]
        # Mirror cuves motor
        self.mirror_cuves_motor = ['Z', '$112', 10]  # [axis, g_code_speed, speed]
        self.pin_limit_switch_mirror_cuves = [3]


    def search_word(self, list, word):
        """
        Rearch a word in the list
        """
        for index, element in enumerate(list):
            if word in element:
                return index
# G_CODE management of motors
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
        return self.arduino_motors.read(25)  # Read the first 20 characters for state
    
# G_CODE to control the kinematics of motors

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
        state = str(self.get_motor_state())
        while 'Idle' not in state:
            state = str(self.get_motor_state())
            time.sleep(0.1)
            print(state)

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

    def unlock_motors(self):
        """
        Unlock all the motors.
        """
        g_code = '$X' + '\n'
        self.execute_g_code(g_code)

    def homing(self):
        """
        Do the GRBL homing.
        """
        g_code = '$H' + '\n'
        self.arduino_motors.write(g_code.encode())

# Kinematics of motors 
    def move_motor(self, motor_parameters, distance):
        """
        Move the motor by a specified distance.

        Args:
            motor_parameters (list): Motor parameters [axis, speed, movement type].
            distance (float): Distance to move.
        """
        gcode = "G0" + motor_parameters[0] + str(distance) + '\n'
        print(gcode)
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

# Initialization of Arduino  

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

    def wait_sensor(self, digital_value, pin):
        """
        Attend que le capteur change d'état
        """
        while digital_value is True:
            digital_value = self.arduino_sensors.digital[pin].read()
            print("The motor don't touch the : ", digital_value)
            time.sleep(0.1)

# Initialization of all motors 

    def initialize_mirror_position(self):
        """
        Initialize the mirror position based on a specific requirement.

        Args:
            pin_mirror (list): Digital pin for the mirror position.
        """
        pin = self.pin_limit_switch_mirror_cuves[0]
        state = self.arduino_sensors.digital[pin].read()
        self.unlock_motors()
        time.sleep(1) 
        if state is True:            
            self.unlock_motors()
            self.execute_g_code('G90\n')            
            self.move_mirror_motor(1)

            while state is True:
                print("Cuvette 1 not reached because ", state)
                state = self.arduino_sensors.digital[pin].read()
                print(self.get_position_xyz())
            
            pos_y = self.get_position_xyz()[2]
            self.move_mirror_motor(distance=pos_y)
            print(pos_y)
        else:
            print("Cuvette 1 is reached")

    def initialisation_motor_slits(self, slit):
        """
        Initialize the motor that controls the 
        variable slit system.
        """
        pin = self.pin_limit_switch_slits[0]
        digital_value = self.arduino_sensors.digital[pin].read()
        time.sleep(1)
        i = -0.005
        print(digital_value)
        if digital_value is False:
            while digital_value is False:
                self.unlock_motors()
                self.move_slits(i)
                digital_value = self.arduino_sensors.digital[pin].read()
                i -= 0.005  # Movement of 0.005 of the motor not optimal
                time.sleep(1)            
            print("Variable slit motor has reached the start")
            self.unlock_motors()
            self.move_slits(i-0.005)
            self.wait_for_idle()
            print("Variable slit motor is ready for measurement")
        else:
            print("Variable slit motor is ready for measurement")
        
        indice = self.search_word(self.name_slits, slit)
        self.move_slits(self.slits_position[indice])
        self.wait_for_idle()


    def initialisation_motor_screw(self):
        """
        Initialize the screw motor for the start of the experiment.
        """
        # pin: limit switch between a mechanical stop of screw 
        # opposite at diffraction grating 
        # we initialize at this position? (question !!!)
        pin = self.pin_limit_switch_screw[0]
        digital_value = self.arduino_sensors.digital[pin].read()
        # we unlock motors because homing cycle is up ($22=1)
        # Why unlock motors in GRBL?
        self.unlock_motors()
        # What is the definition of homing in GRBL?
        self.homing()
        # Loop 
        self.wait_sensor(digital_value, pin)
            
        print("We are back to the start!")
        
        self.wait_sensor(digital_value, pin)

        print("Diffraction grating is ready for acquisition!")
        # End-of-file (EOF)

    def initialisation_motors(self, slip):
        """
        Initializes all motors to start an acquisition.
        """
        self.initialize_end_stop(self.all_pin)
        time.sleep(1)
        self.initialize_mirror_position()
        self.wait_for_idle()
        self.initialisation_motor_screw()
        self.wait_for_idle()
        self.initialisation_motor_slits(slip)

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
    motors_controller.unlock_motors() 
  
    motors_controller.move_screw(0.1)