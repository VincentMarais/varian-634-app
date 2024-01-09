# Motors config

Pour tester le code Python des moteurs :

1. Assurez-vous que le code "grbl.ino" a été téléversé sur la carte Arduino avec la CNC shield.

2. Ouvrez le terminal série de l'Arduino en tapant la commande suivante : "$$"

3. Assurez-vous que les paramètres si-dessous sont correctement configurés avant de tester les moteurs
```
$0=10
$1=25
$2=0
$3=0
$4=0
$5=0
$6=0
$10=1
$11=0.010
$12=0.002
$13=0
$20=0
$21=1
$22=1
$23=0
$24=10.000
$25=12.000
$26=250
$27=1.000
$30=1000
$31=0
$32=0
$100=10295.660
$101=3200.000
$102=3200.000
$110=10.000
$111=10.000
$112=10.000
$120=200.000
$121=10.000
$122=10.000
$130=21.000
$131=800.000
$132=800.000

```

## Code pour tester mirror_cuves_motor.py 
```
import serial  
from pyfirmata import Arduino, util, INPUT

# INITIALISATION MOTEUR:

COM_PORT_MOTORS = 'COM3'
COM_PORT_SENSORS = 'COM6'
BAUD_RATE = 115200
INITIALIZATION_TIME = 2

arduino_motors = serial.Serial(COM_PORT_MOTORS, BAUD_RATE)
arduino_motors.write("\r\n\r\n".encode()) # encode pour convertir "\r\n\r\n" 
time.sleep(INITIALIZATION_TIME)   # Attend initialisation un GRBL
arduino_motors.flushInput()  # Vider le tampon d'entrée, en supprimant tout son contenu.

# INITIALISATION Forche optique:

arduino_optical_fork = Arduino(COM_PORT_SENSORS)

# Test move_mirror_cuves_motor
move_mirror_cuves_motor(arduino_motors, plastic_disc_position=0.4)
initialisation_mirror_cuves_motor(arduino_motors=arduino_motors, arduino_optical_fork=arduino_optical_fork)
initialisation_mirror_cuves_motor_v2(arduino_motors=arduino_motors, arduino_optical_fork=arduino_optical_fork)
```

## Code pour tester screw_motor.py 


```

import serial  
from pyfirmata import Arduino, util, INPUT

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
# INITIALISATION end-stop:

arduino_end_stop = Arduino(COM_PORT_SENSORS)

screw_controller = ScrewController(arduino_motors, arduino_end_stop)

#screw_controller.move_screw(distance=-2)
screw_controller.initialize_screw()
```
## slits motor.py

```
import serial  
from pyfirmata import Arduino, util, INPUT
# INITIALISATION MOTEUR:

COM_PORT_MOTORS = 'COM3'
COM_PORT_SENSORS = 'COM9'
BAUD_RATE = 115200
INITIALIZATION_TIME = 2

arduino_motors = serial.Serial(COM_PORT_MOTORS, BAUD_RATE)
arduino_motors.write("\r\n\r\n".encode()) # encode pour convertir "\r\n\r\n" 
time.sleep(INITIALIZATION_TIME)   # Attend initialisation un GRBL
arduino_motors.flushInput()  # Vider le tampon d'entrée, en supprimant tout son contenu.

# INITIALISATION Forche optique:

arduino_optical_fork = Arduino(COM_PORT_SENSORS)
g_code='$X' + '\n'
arduino_motors.write(g_code.encode())
# Test move_mirror_cuves_motor
move_slits(arduino_motors=arduino_motors)

```

## all_motors.py

```
import serial  

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
# INITIALISATION end-stop:

g_code= "?" + '\n'
general_motors_controller=GeneralMotorsController(arduino_motors)
general_motors_controller.execute_g_code(g_code)
print(general_motors_controller.get_position_xyz()[0])

```