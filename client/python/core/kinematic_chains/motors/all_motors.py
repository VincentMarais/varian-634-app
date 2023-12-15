"""
This program controls all the motors present on the VARIAN 634.
"""
import time
import re

def state_motors(arduino_motors):
    """
    Purpose: Determine the state of all motors on the VARIAN 634, 
    whether a motor is in "Run" or "Idle" mode.

    Input:
        arduino_motors (serial.Serial): Characterization of the motor Arduino connected to the screw
     

    Output:
        - Returns the first 10 characters of the motor's state.

    """
    g_code = '?' + '\n'
    arduino_motors.write(g_code.encode())
    return arduino_motors.read(40)  # 10: We read the first 10 characters from the serial

def grbl_parameter_motors(arduino_motors):
    """
    Purpose: Display the type of motor movement: G90 for absolute displacement.

    Input:
        arduino_motors (serial.Serial): Characterization of the motor Arduino connected to the screw

    Output: None

    """
    g_code = '$G' + '\n'
    arduino_motors.write(g_code.encode())
    print(arduino_motors.read(75))  # 75 because the information about G90 is at this position

def stop_motors(arduino_motors):
    """
    Purpose: Function that forcefully stops the motors.

    Input:
        arduino_motors (serial.Serial): Characterization of the motor Arduino connected to the screw

    """

    g_code = '!' + '\n'
    arduino_motors.write(g_code.encode())

def cycle_resumption(arduino_motors):
    """
    Purpose: reprise d’une commande des motors après la commande "!".

    Input:
        arduino_motors (serial.Serial): Characterization of the motor Arduino connected to the screw

    """

    g_code = '~' + '\n'
    arduino_motors.write(g_code.encode())

def wait_for_motor_idle(arduino_motors):
    """
    Purpose: Wait for the motors to be at rest, i.e., in 'Idle' mode.

    Input:
        arduino_motors (serial.Serial): Characterization of the motor Arduino connected to the screw

    """
    gcode_state_motor = str(state_motors(arduino_motors))
    while 'Idle' not in gcode_state_motor:
        gcode_state_motor = str(state_motors(arduino_motors))
    print(gcode_state_motor)

def position_xyz(arduino_motors):
    """
    Purpose: Donner la positions des moteurs

    Input:
        arduino_motors (serial.Serial): Characterization of the motor Arduino connected to the screw

    Output :

    """
    g_code= "?" + '\n' 
    arduino_motors.write(g_code.encode())
    time.sleep(0.1)

    # Lire et traiter la réponse
    response = str(arduino_motors.readline())
    print("Réponse brute :", response)
    while 'MPos' not in response:
        response = str(arduino_motors.readline())    
        # Extraire les coordonnées X, Y, et Z
    match = re.search(r"MPos:([-+]?[0-9]*\.?[0-9]+),([-+]?[0-9]*\.?[0-9]+),([-+]?[0-9]*\.?[0-9]+)", response)        
    x_pos, y_pos, z_pos = [float(coordinate) for coordinate in match.groups()]
    
    return x_pos, y_pos, z_pos
# End-of-file (EOF)
