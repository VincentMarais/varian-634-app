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

sensor_data_running = False

def sensor_data_task():
    global sensor_data_running, wavelength_min, wavelength_max, step
    sensor_data_running = True
    print("Generating sensor values")
    number_measurements = int((wavelength_max - wavelength_min) / step)
    print("number_measurements:", number_measurements)
    for i in range(number_measurements + 1):
        if not sensor_data_running:
            print("Stopping sensor data generation")
            break
        time.sleep(1)
        data = ser.readline().decode('utf-8').rstrip()
        if data:
            print("Data:", data)
            socketio.emit('updateSensorData', {'value': data, "index": i})


@socketio.on('startSensorData')
def handle_start_sensor_data():
    global wavelength_min, wavelength_max, step, sensor_data_running, selected_cuvette, selected_slits
    # Vérifiez si tous les paramètres nécessaires sont définis et valides
    if None in (wavelength_min, wavelength_max, step) or not selected_cuvette or not selected_slits:
        error_msg = "Cannot start sensor data generation: One or more parameters are not set or invalid."
        print(error_msg)
        socketio.emit('error', {'message': error_msg})
        return

    # Ajoutez ici des vérifications supplémentaires pour la validité des paramètres si nécessaire

    # Si tout est valide, démarrez la génération des données de capteur
    print("Starting sensor data generation")
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
    print(f'Received Wavelength Params: Min = {wavelength_min}, Max = {wavelength_max}, Step = {step}, Cuvette = {selected_cuvette}, Slits = {selected_slits}')
    # Vous pouvez ici ajouter la logique pour valider les paramètres si nécessaire.

@socketio.on('stopSensorData')
def handle_stop_sensor_data():
    global sensor_data_running
    sensor_data_running = False  # Cela indiquera à la boucle de s'arrêter
    print("Received stop signal")



@app.route('/')


@socketio.on('connect')
def connect():
    """
    Decorator for connect
    """
    global thread
    print('Client connected', request.sid)

    


@socketio.on('disconnect')
def disconnect():
    """
    Decorator for disconnect
    """
    print('Client disconnected',  request.sid)

if __name__ == '__main__':
    socketio.run(app)