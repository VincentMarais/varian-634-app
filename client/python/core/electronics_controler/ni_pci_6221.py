"""
This program allows reading the voltage across the photodiodes using an NI-PCI 6221 card.
Doc NI-PCI 6221
https://www.ni.com/docs/fr-FR/bundle/pci-pxi-usb-6221-specs/page/specs.html

"""
import time
import numpy as np
import nidaqmx
from nidaqmx.constants import AcquisitionType, TerminalConfiguration
from pyfirmata import util, INPUT

class VoltageAcquisition:
    """
    class program allows reading the voltage across the photodiodes using an NI-PCI 6221 card.
    """
    def __init__(self):
        """
        Initialise une instance de la classe VoltageAcquisition.

        Paramètres :
        - channels : Liste des canaux d'acquisition (par exemple, ['Dev1/ai0', 'Dev1/ai1']).
        - sample_rate : Taux d'échantillonnage en échantillons par seconde (Hz).
        - samples_per_channel : Nombre d'échantillons à acquérir par canal.

        """
        # voltage acquisition parameters 
        self.channels = ['Dev1/ai0', 'Dev1/ai1']  
        self.samples_per_channel = 250000 # sampling frequency
        self.sample_rate = 30000 # 

        # Characteristics of square wave (xenon arc lamp control signal)
        self.frequency = np.array([20.0])
        self.duty_cycle = np.array([0.5])
        self.device='/Dev1/ctr0'


    def configure_task_voltage(self, task, channel):
        """
        Configure la tâche de mesure de tension analogique.

        Paramètres :
        - task : Objet de tâche nidaqmx.
        - channel : Canal d'entrée analogique à configurer (par exemple, 'Dev1/ai0').

        """
        task.ai_channels.add_ai_voltage_chan(channel, terminal_config=TerminalConfiguration.DIFF)
        task.timing.cfg_samp_clk_timing(self.sample_rate, samps_per_chan=self.samples_per_channel, sample_mode=AcquisitionType.FINITE)
        
            
    def configure_task_impulsion(self, task):
        """
        Configure la tâche de génération d'impulsion.

        Paramètres :
        - task : Objet de tâche nidaqmx.
        - frequency : Fréquence de l'impulsion en hertz (Hz).
        - duty_cycle : Cycle de service de l'impulsion (entre 0 et 1, où 1 est à 100%).
        - device : Nom du périphérique de compteur à utiliser (par défaut, '/Dev1/ctr0').

        """
        task.co_channels.add_co_pulse_chan_freq(self.device, freq=self.frequency[0], duty_cycle=self.duty_cycle, initial_delay=0.0)
        task.timing.cfg_implicit_timing(sample_mode=AcquisitionType.CONTINUOUS)
        task.start()
    
    def measure_voltage(self, task, channel):
        voltages=[]
        self.configure_task_voltage(task, channel)        # Acquisition des données
        voltages = task.read(number_of_samples_per_channel=self.samples_per_channel)                
        task.stop()
        return voltages

    def measure_mean_voltage(self, task):
        min_voltages=[]
        frequence = int(self.frequency[0])
        for _ in range(frequence):
                # Acquisition des données
            data = task.read(number_of_samples_per_channel=self.samples_per_channel)
            # Conversion des données en un tableau numpy pour faciliter les calculs
            np_data = np.array(data)
                
                # Trouver et stocker le minimum
            min_voltage = np.min(np_data)
            min_voltages.append(min_voltage)
        task.stop()
        mean = np.mean(min_voltages)
        return mean
        
    def acquire_data_voltages_chemical_kinetics(self, time_acquisition, delay_between_measurements):
        """
        Acquiert les tensions minimales à partir de la tâche de mesure de tension.

        Paramètres :
        - task : Objet de tâche nidaqmx.
        - frequency : Fréquence de lecture de données (nombre d'acquisitions par seconde).
        - time_acquisition : Durée d'acquisition en secondes (facultatif).

        Retourne :
        - min_voltages : Liste des tensions minimales mesurées.

        """
        voltages = []
        temps = [0]
        
        with nidaqmx.Task() as read_voltage :
            start_time = time.time()

            while time.time() - start_time < time_acquisition:  # Boucle pendant la durée spécifiée
                start_time_temp=time.time()
                # Acquisition des données
                data=self.measure_mean_voltage(read_voltage)
                voltages.append(data)
                intant_time=time.time() - start_time_temp
                while intant_time < delay_between_measurements:
                    intant_time+= time.time() - start_time_temp
                temps.append(intant_time)            
            read_voltage.stop()
        return temps, voltages

    def voltage_acquisition_scanning_baseline(self, channel):
        """
        Effectue l'acquisition de tension en fonction du type de tâche.

        Paramètres :
        - task_type : Type de tâche ('scanning' ou 'chemical_kinetics').
        - frequency : Fréquence de l'impulsion en hertz (Hz).
        - duty_cycle : Cycle de service de l'impulsion (entre 0 et 1, où 1 est à 100%).
        - channel : Index du canal à acquérir.
        - time_acquisition : Durée d'acquisition en secondes (facultatif).

        Retourne :
        - Moyenne des tensions minimales mesurées.

        """
        with nidaqmx.Task() as task_voltage, nidaqmx.Task() as task_impulsion:
            self.configure_task_impulsion(task_impulsion)
            self.configure_task_voltage(task_voltage, self.channels[channel])
            min_voltages = self.measure_mean_voltage(task_voltage)
            task_impulsion.stop()
            task_voltage.stop()
        return min_voltages
    
    def voltage_acquisition_chemical_kinetics(self, channel, time_acquisition, time_per_acquisition):
        """
        Effectue l'acquisition de tension en fonction du type de tâche.

        Paramètres :
        - task_type : Type de tâche ('scanning' ou 'chemical_kinetics').
        - frequency : Fréquence de l'impulsion en hertz (Hz).
        - duty_cycle : Cycle de service de l'impulsion (entre 0 et 1, où 1 est à 100%).
        - channel : Index du canal à acquérir.
        - time_acquisition : Durée d'acquisition en secondes (facultatif).

        Retourne :
        - Moyenne des tensions minimales mesurées.

        """
        with nidaqmx.Task() as task_voltage, nidaqmx.Task() as task_impulsion:
            self.configure_task_impulsion(task_impulsion)
            self.configure_task_voltage(task_voltage, self.channels[channel])
            voltages = self.acquire_data_voltages_chemical_kinetics(time_acquisition, time_per_acquisition)
            task_impulsion.stop()
            task_voltage.stop()
        return voltages
    
    def sensors_state(self, board, pin):
        """
        Program give the digital state of and sensor :
            True or False
        """
    # Configurer le port digital 3 en tant qu'entrée
        board.digital[pin].mode = INPUT  # Modifié ici

    # Créer une instance d'Itérateur pour ne pas manquer les données entrantes
        it = util.Iterator(board)
        it.start()

        # Permettre à l'itérateur de démarrer
        time.sleep(1)

        while True:
            # Lire la valeur du port digital 3
            digital_value = board.digital[pin].read()

            # Afficher la valeur
            print(f"Valeur lue sur le port digital {pin} :", digital_value)

            # Attendre un peu avant de lire à nouveau
            time.sleep(0.1)

if __name__ == "__main__":
    acqui_voltage=VoltageAcquisition()

    from pyfirmata import Arduino
    #Arduino
    BOARD = Arduino('COM9')
    PIN_SENSOR = 2
    acqui_voltage.sensors_state(BOARD, PIN_SENSOR)
    
    import matplotlib.pyplot as plt

    #NI PCI 6221
    TASK = nidaqmx.Task()
    CHANNEL = 'ai3'

    data_y=acqui_voltage.measure_voltage(TASK, CHANNEL)
    x_data= np.arange(0, len(data_y), 1)
    plt.plot(x_data, data_y)
    plt.xlabel('samples')
    plt.ylabel('Voltage (Volt)')
    plt.legend()  
    plt.grid()
    plt.tight_layout()      
    plt.show()


# Utilisation de la classe
#channels = ['Dev1/ai0', 'Dev1/ai1']
#acquisition = VoltageAcquisition(channels, sample_rate, samples_per_channel)
#mean_voltage = acquisition.perform_voltage_acquisition(task_type, frequency, duty_cycle, channel, time_acquisition)

