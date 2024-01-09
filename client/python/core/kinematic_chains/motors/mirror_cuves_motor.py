"""
The pilot program controls the mirror-linked engine, allowing the 
transition from the sample chamber to the reference chamber.

"""
import time
from pyfirmata import INPUT
from all_motors import  GeneralMotorsController

#kinematic_chains.motors.all_motors

class MirrorCuvesController:
    """
    class : pilot program controls the mirror-linked engine, allowing the 
    transition from the sample chamber to the reference chamber
    """
    def __init__(self, arduino_motors, arduino_optical_fork):
        """
        Initialize the controller with motor and optical fork instances.

        Args:
            arduino_motors: An instance of the Arduino controlling the mirror motors.
            arduino_optical_fork: An instance of the Arduino controlling the optical fork sensor.
        """
        self.arduino_motors = arduino_motors
        self.arduino_optical_fork = arduino_optical_fork
        self.initialize_optical_fork()
        self.general_motors_controller=GeneralMotorsController(self.arduino_motors)

    def initialize_optical_fork(self):
        """
        Set up the optical fork sensor as an input device.
        """
        self.arduino_optical_fork.digital[3].mode = INPUT
        time.sleep(1)

    def move_mirror_motor(self, position):
        """
        Move the mirror motor to a specified position.

        Args:
            position: The desired position to which the mirror motor should be moved.
        """
        self.general_motors_controller.execute_g_code('$X' + '\n')
        self.general_motors_controller.execute_g_code('G0Y' + str(position))

    def initialize_mirror_position(self):
        """
        Find and set the initial position of the mirror using the optical fork.
        """
        general_motors_controller=GeneralMotorsController(self.arduino_motors)

        while self.arduino_optical_fork.digital[3].read():
            self.move_mirror_motor(0.4)
        general_motors_controller.stop_motors(self.arduino_motors)  # Assuming 'stop_motors' function is defined elsewhere.

    def initialize_mirror_position_v2(self):
        """
        An alternative method to initialize the mirror position based on a specific requirement.
        """
        self.move_mirror_motor(position=2)
        #state=self.arduino_optical_fork.digital[3].read()
        while state is True:
            print("Cuve 1 non atteinte car ", state)
            state=self.arduino_optical_fork.digital[3].read()

        pos_y = self.general_motors_controller.get_position_xyz()[1]
        self.move_mirror_motor(position=pos_y)
        print(pos_y)

    def execute_g_code(self, g_code):
        """
        Send a G-code command to the motor.

        Args:
            g_code: The G-code command to be sent to the motor.
        """
        self.arduino_motors.write(f'{g_code}\n'.encode())
# End-of-file (EOF)

import serial  
from pyfirmata import Arduino, INPUT

# INITIALISATION MOTEUR:

COM_PORT_MOTORS = 'COM3'
COM_PORT_SENSORS = 'COM9'
BAUD_RATE = 115200
INITIALIZATION_TIME = 2

arduino_motors = serial.Serial(COM_PORT_MOTORS, BAUD_RATE)
arduino_motors.write("\r\n\r\n".encode()) # encode pour convertir "\r\n\r\n" 
time.sleep(INITIALIZATION_TIME)   # Attend initialisation un GRBL
arduino_motors.flushInput()  # Vider le tampon d'entrée, en supprimant tout son contenu.
g_code='$X' + '\n'
arduino_motors.write(g_code.encode())
# INITIALISATION end-stop :

arduino_optical_fork = Arduino(COM_PORT_SENSORS)

screw_controller = MirrorCuvesController(arduino_motors, arduino_optical_fork)

screw_controller.move_mirror_motor(position=-2)
#screw_controller.initialize_mirror_position_v2()