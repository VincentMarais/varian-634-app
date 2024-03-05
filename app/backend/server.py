import time
from datetime import datetime
from threading import Lock
from flask import Flask, request
from flask_socketio import SocketIO
import serial


thread = None
thread_lock = Lock()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'VARIAN634!'
socketio = SocketIO(app, cors_allowed_origins='*')
ser = serial.Serial('COM4', 9600, timeout=1)

sensor_data_running = False


# Initialisation des variables globales pour stocker les paramètres
wavelength_min = None
wavelength_max = None
step = None
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


def sensor_data_task():
    global sensor_data_running, wavelength_min, wavelength_max, step
    sensor_data_running = True
    print("Génération des valeurs du capteur")
    number_measurements = int((wavelength_max - wavelength_min) / step)
    print("nombre_mesures:", number_measurements)
    for i in range(number_measurements + 1):
        if not sensor_data_running:
            print("Arrêt de la génération des données du capteur")
            break
        time.sleep(1)
        data = ser.readline().decode('utf-8').rstrip()
        if data:
            print("Données:", data)
            socketio.emit('updateSensorData', {'value': data, "index": i})


@socketio.on('startSensorData')
def handle_start_sensor_data():
    global wavelength_min, wavelength_max, step, sensor_data_running, selected_cuvette, selected_slits
    if None in (wavelength_min, wavelength_max, step) or not selected_cuvette or not selected_slits:
        error_msg = "Impossible de démarrer la génération de données du capteur : un ou plusieurs paramètres ne sont pas définis ou invalides."
        print(error_msg)
        socketio.emit('error', {'message': error_msg})
        return

    print("Début de la génération de données du capteur")
    sensor_data_running = True
    sensor_data_task()  # Démarrage effectif de la génération de données

@socketio.on('setWaveLengthParams')
def handle_set_wave_length_params(json):
    global wavelength_min, wavelength_max, step, selected_cuvette, selected_slits
    wavelength_min = float(json['wavelengthMin'])
    wavelength_max = float(json['wavelengthMax'])
    step = float(json['step'])
    selected_cuvette = json.get('selectedCuvette', '')
    selected_slits = json.get('selectedSlits', [])
    print(f'Paramètres de longueur d\'onde reçus : Min = {wavelength_min}, Max = {wavelength_max}, Pas = {step}, Cuvette = {selected_cuvette}, Lames = {selected_slits}')

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