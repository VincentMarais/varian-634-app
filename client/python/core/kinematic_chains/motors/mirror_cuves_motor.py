"""
The pilot program controls the mirror-linked engine, allowing the 
transition from the sample chamber to the reference chamber.

"""
import time
from pyfirmata import INPUT
from kinematic_chains.motors.all_motors import stop_motors, position_xyz
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
        self.execute_g_code('$X\nG91\nG0Y' + str(position))

    def initialize_mirror_position(self):
        """
        Find and set the initial position of the mirror using the optical fork.
        """
        while self.arduino_optical_fork.digital[3].read():
            self.move_mirror_motor(0.4)
        stop_motors(self.arduino_motors)  # Assuming 'stop_motors' function is defined elsewhere.

    def initialize_mirror_position_v2(self):
        """
        An alternative method to initialize the mirror position based on a specific requirement.
        """
        self.execute_g_code('$X\nG90\nG0Y1')
        while self.arduino_optical_fork.digital[3].read():
            print("Cuve 1 non atteinte")
        pos_y = position_xyz(self.arduino_motors)[1]
        self.execute_g_code("G0Y" + str(pos_y))
        print(pos_y)

    def execute_g_code(self, g_code):
        """
        Send a G-code command to the motor.

        Args:
            g_code: The G-code command to be sent to the motor.
        """
        self.arduino_motors.write(f'{g_code}\n'.encode())
# End-of-file (EOF)
