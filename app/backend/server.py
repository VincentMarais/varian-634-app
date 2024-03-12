import time
from datetime import datetime
from threading import Lock
from flask import Flask, request
from flask_socketio import SocketIO
import serial
from core.acquisition_mode import Varian634AcquisitionMode
from pyfirmata import Arduino


# INITIALIZATION MOTOR:

COM_PORT_MOTORS = 'COM3'
COM_PORT_SENSORS = 'COM9'
BAUD_RATE = 115200
INITIALIZATION_TIME = 2

arduino_motors = serial.Serial(COM_PORT_MOTORS, BAUD_RATE)
arduino_motors.write("\r\n\r\n".encode())  # encode to convert "\r\n\r\n"
time.sleep(INITIALIZATION_TIME)  # Wait for initialization of GRBL
arduino_motors.flushInput()  # Clear the input buffer by discarding its current contents.

# INITIALIZATION Optical Fork:

arduino_sensors = Arduino(COM_PORT_SENSORS)
SAMPLE_NAME = "Bromophenol" 
    
USER_PATH =  "C:\\Users\\vimarais\\Documents\\Analyse"



thread = None
thread_lock = Lock()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'VARIAN634!'
socketio = SocketIO(app, cors_allowed_origins='*')
baseline_scanning = Varian634AcquisitionMode(arduino_motors, arduino_sensors, socketio, SAMPLE_NAME, "cuvette 2", "Fente_1nm")

sensor_data_running = False


# Initialisation des variables globales pour stocker les paramètres
wavelength_min = None
wavelength_max = None
step_wavelength = None
selected_cuvette = None
selected_slit = None


@socketio.on('setComPort')
def handle_set_com_port(data):
    com_port = data['comPort']
    print('Received COM Port:', com_port)



def get_current_datetime():
    """
    Get current date time
    """
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S")




def scanning_mode():
    global sensor_data_running, wavelength_min, wavelength_max, step_wavelength
    sensor_data_running = True
    baseline_scanning.acquisition(wavelength_min, wavelength_max, step_wavelength)



@socketio.on('startSensorData')
def handle_start_sensor_data():
    global wavelength_min, wavelength_max, step_wavelength, sensor_data_running, selected_cuvette, selected_slits
    if None in (wavelength_min, wavelength_max, step_wavelength) or not selected_cuvette or not selected_slits:
        error_msg = "Impossible de démarrer la génération de données du capteur : un ou plusieurs paramètres ne sont pas définis ou invalides."
        print(error_msg)
        socketio.emit('error', {'message': error_msg})
        return

    print("Début de la génération de données du capteur")
    sensor_data_running = True
    scanning_mode()  # Démarrage effectif de la génération de données

@socketio.on('setScanningParams')
def handle_set_wave_length_params(json):
    global wavelength_min, wavelength_max, step_wavelength, selected_cuvette, selected_slits
    wavelength_min = float(json['wavelengthMin'])
    wavelength_max = float(json['wavelengthMax'])
    step_wavelength = float(json['step'])
    selected_cuvette = json.get('selectedCuvette', '')
    selected_slits = json.get('selectedSlits', [])
    print(f'Paramètres de longueur d\'onde reçus : Min = {wavelength_min}, Max = {wavelength_max}, Pas = {step_wavelength}, Cuvette = {selected_cuvette}, Lames = {selected_slits}')

@socketio.on('stopSensorData')
def handle_stop_sensor_data():
    global sensor_data_running
    sensor_data_running = False  # Cela indiquera à la boucle de s'arrêter
    print("Signal d'arrêt reçu")

@app.route('/')
def index():
    return "Bienvenue sur le serveur" 

if __name__ == '__main__':
    socketio.run(app)