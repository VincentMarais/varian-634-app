# Test core programs

## Baseline.py

1. Fonction initialize_measurement

```
import serial  
from pyfirmata import Arduino

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

arduino_sensors = Arduino(COM_PORT_SENSORS)

initialize_measurement(arduino_motors=arduino_motors, arduino_sensors=arduino_sensors, screw_translation_speed=10)

```


2. perform_step_measurement_baseline

```
import numpy as np
import serial  
# INITIALISATION MOTEUR:

COM_PORT_MOTORS = 'COM3'
COM_PORT_SENSORS = 'COM6'
BAUD_RATE = 115200
INITIALIZATION_TIME = 2

arduino_motors = serial.Serial(COM_PORT_MOTORS, BAUD_RATE)
arduino_motors.write("\r\n\r\n".encode()) # encode pour convertir "\r\n\r\n" 
time.sleep(INITIALIZATION_TIME)   # Attend initialisation un GRBL
arduino_motors.flushInput()  # Vider le tampon d'entrée, en supprimant tout son contenu.

# INITIALISATION carte NI-PCI 6221:
Frequence_creneau = np.array([20.0])
Rapport_cyclique = np.array([0.5])
SAMPLES_PER_CHANNEL = 30000
SAMPLE_RATE = 250000
CHANNELS = ['Dev1/ai0', 'Dev1/ai1']  

print(perform_step_measurement_baseline(arduino_motors=arduino_motors, samples_per_channel=SAMPLES_PER_CHANNEL, sample_rate=SAMPLE_RATE, pulse_frequency=Frequence_creneau, channels=CHANNELS))

```

3. calculate_wavelength
```
print(calculate_wavelength(0))

```


4. precision_mode_baseline

```
import numpy as np
import serial 
from pyfirmata import Arduino

# INITIALISATION MOTEUR:

COM_PORT_MOTORS = 'COM3'
COM_PORT_SENSORS = 'COM9'
BAUD_RATE = 115200
INITIALIZATION_TIME = 2

arduino_motors = serial.Serial(COM_PORT_MOTORS, BAUD_RATE)
arduino_motors.write("\r\n\r\n".encode()) # encode pour convertir "\r\n\r\n" 
time.sleep(INITIALIZATION_TIME)   # Attend initialisation un GRBL
arduino_motors.flushInput()  # Vider le tampon d'entrée, en supprimant tout son contenu.

# INITIALISATION carte NI-PCI 6221:
Frequence_creneau = np.array([20.0])
Rapport_cyclique = np.array([0.5])
SAMPLES_PER_CHANNEL = 30000
SAMPLE_RATE = 250000
CHANNELS = ['Dev1/ai0', 'Dev1/ai1']  

# INITIALISATION Forche optique:

arduino_sensors = Arduino(COM_PORT_SENSORS)

print(precision_mode_baseline(arduino_motors=arduino_motors, screw_travel=5, number_measurements=5, screw_translation_speed=10, pulse_frequency=Frequence_creneau, samples_per_channel=SAMPLES_PER_CHANNEL, sample_rate=SAMPLE_RATE, channels=CHANNELS))



```

# acquisition

```

import numpy as np
import serial 
from pyfirmata import Arduino

# INITIALISATION MOTEUR:

COM_PORT_MOTORS = 'COM3'
COM_PORT_SENSORS = 'COM9'
BAUD_RATE = 115200
INITIALIZATION_TIME = 2

arduino_motors = serial.Serial(COM_PORT_MOTORS, BAUD_RATE)
arduino_motors.write("\r\n\r\n".encode()) # encode pour convertir "\r\n\r\n" 
time.sleep(INITIALIZATION_TIME)   # Attend initialisation un GRBL
arduino_motors.flushInput()  # Vider le tampon d'entrée, en supprimant tout son contenu.

# INITIALISATION carte NI-PCI 6221:
Frequence_creneau = np.array([20.0])
Rapport_cyclique = np.array([0.5])
SAMPLES_PER_CHANNEL = 30000
SAMPLE_RATE = 250000
CHANNELS = ['Dev1/ai0', 'Dev1/ai1']  

# INITIALISATION Forche optique:

arduino_sensors = Arduino(COM_PORT_SENSORS)


baseline_acquisition(arduino_motors=arduino_motors, arduino_sensors=arduino_sensors, screw_travel=3, number_measurements=3, screw_translation_speed=10, pulse_frequency=Frequence_creneau, duty_cycle=Rapport_cyclique, samples_per_channel=SAMPLES_PER_CHANNEL, sample_rate=SAMPLE_RATE, channels=CHANNELS)


```