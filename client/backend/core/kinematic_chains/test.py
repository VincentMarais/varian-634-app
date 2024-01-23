import serial
import time
from motors_varian_634 import GeneralMotorsController
from pyfirmata import util, INPUT, Arduino
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

    # 
motors_controller.set_motors_speed(motors_controller.screw_motor, 10)  # Set screw motor speed to 10

# Test get_motor_state function
motor_state = motors_controller.get_motor_state()
print("Motors State:", motor_state)

    # Test display_grbl_parameter function
motors_controller.display_grbl_parameter()

    # Test get_position_xyz function
current_position = motors_controller.get_position_xyz()
print("Current Position of motors:", current_position)   

    # Test move_mirror_motor function
motors_controller.move_screw(-5)  # Move screw motor by 3 units

    # Test move_screw function

    
