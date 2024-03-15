from threading import Lock
from flask import Flask
from flask_socketio import SocketIO
import serial
from test_app import Varian634ATestApp
from pyfirmata import Arduino


# INITIALIZATION HARDWARE:
COM_PORT_MOTORS = 'COM8'
COM_PORT_SENSORS = 'COM10'
BAUD_RATE = 9600
INITIALIZATION_TIME = 2

arduino_motors = serial.Serial(COM_PORT_MOTORS, BAUD_RATE)
arduino_sensors = serial.Serial(COM_PORT_SENSORS, BAUD_RATE, timeout=1)

# INITIALIZATION Optical Fork:
SAMPLE_NAME = "Bromophenol"

# Initialisation serveur 
thread = None
thread_lock = Lock()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'VARIAN634!'
socketio = SocketIO(app, cors_allowed_origins='*')

# Initialisation MODE d'acquisition Varian634

sensor_data_running = False
sensor_data_should_stop = False  


# Initialisation des variables globales pour stocker les paramètres du mode scanning
wavelength_min = None
wavelength_max = None
step_wavelength = None
selected_cuvette = None
selected_slits = None
sample_name = None



@socketio.on('setScanningParams')
def handle_set_wave_length_params(json):
    global wavelength_min, wavelength_max, step_wavelength, selected_cuvette, selected_slits, sample_name
    wavelength_min = float(json['wavelengthMin'])
    wavelength_max = float(json['wavelengthMax'])
    step_wavelength = float(json['step'])
    selected_cuvette = json['selectedCuvette'][:]
    selected_slits = json['selectedSlits']
    sample_name = json['sampleName']
    print(f'Paramètres de longueur d\'onde reçus : Min = {wavelength_min}, Max = {wavelength_max}, Pas = {step_wavelength}, Cuvette = {selected_cuvette}, Fentes = {selected_slits}, Nom échantillon = {sample_name}')


# Initialisation des variables globales pour stocker les paramètres du mode cinétique
def scanning_mode():
    global sensor_data_running, wavelength_min, wavelength_max, step_wavelength, selected_cuvette, selected_slits, sample_name
    sensor_data_running = True
    sensor_data_should_stop = False  # Réinitialiser pour une nouvelle exécution
    
    for slit in selected_slits:
        if sensor_data_should_stop:
            break  # Sortie anticipée si un arrêt est demandé       
        baseline_scanning = Varian634ATestApp(arduino_motors, arduino_sensors, socketio, sample_name, selected_cuvette, slit)
        baseline_scanning.acquisition(wavelength_min, wavelength_max, step_wavelength)

    sensor_data_running = False  # Assurez-vous de réinitialiser cela auss
    
@socketio.on('startSensorData')
def handle_start_sensor_data():
    global wavelength_min, wavelength_max, step_wavelength, sensor_data_running, selected_cuvette, selected_slits
    if None in (wavelength_min, wavelength_max, step_wavelength) or not selected_cuvette or not selected_slits:
        error_msg = "Impossible de démarrer la génération de données du capteur : un ou plusieurs paramètres ne sont pas définis ou invalides."
        print(error_msg)
        socketio.emit('error', {'message': error_msg})
        return

    print("Début du mode scanning")
    sensor_data_running = True
    scanning_mode()  # Démarrage effectif de la génération de données

@socketio.on('stopSensorData')
def handle_stop_sensor_data():
    global sensor_data_should_stop
    sensor_data_should_stop = True
    print("Arrêt du mode scanning demandé")

@app.route('/')
def index():
    return "Bienvenue sur le serveur" 

if __name__ == '__main__':
    socketio.run(app)