"""
This program allows reading the voltage across the photodiodes using an NI-PCI 6221 card.
Doc NI-PCI 6221
https://www.ni.com/docs/fr-FR/bundle/pci-pxi-usb-6221-specs/page/specs.html

"""
import time
import numpy as np
import nidaqmx
from nidaqmx.constants import AcquisitionType, TerminalConfiguration

class VoltageAcquisition:
    """
    class program allows reading the voltage across the photodiodes using an NI-PCI 6221 card.
    """
    def __init__(self, channels, sample_rate, samples_per_channel):
        """
        Initialise une instance de la classe VoltageAcquisition.

        Paramètres :
        - channels : Liste des canaux d'acquisition (par exemple, ['Dev1/ai0', 'Dev1/ai1']).
        - sample_rate : Taux d'échantillonnage en échantillons par seconde (Hz).
        - samples_per_channel : Nombre d'échantillons à acquérir par canal.

        """
        self.channels = channels
        self.sample_rate = sample_rate
        self.samples_per_channel = samples_per_channel

    def configure_task_voltage(self, task, channel):
        """
        Configure la tâche de mesure de tension analogique.

        Paramètres :
        - task : Objet de tâche nidaqmx.
        - channel : Canal d'entrée analogique à configurer (par exemple, 'Dev1/ai0').

        """
        task.ai_channels.add_ai_voltage_chan(channel, terminal_config=TerminalConfiguration.DIFF)
        task.timing.cfg_samp_clk_timing(self.sample_rate, samps_per_chan=self.samples_per_channel, sample_mode=AcquisitionType.FINITE)

    def configure_task_impulsion(self, task, frequency, duty_cycle, device='/Dev1/ctr0'):
        """
        Configure la tâche de génération d'impulsion.

        Paramètres :
        - task : Objet de tâche nidaqmx.
        - frequency : Fréquence de l'impulsion en hertz (Hz).
        - duty_cycle : Cycle de service de l'impulsion (entre 0 et 1, où 1 est à 100%).
        - device : Nom du périphérique de compteur à utiliser (par défaut, '/Dev1/ctr0').

        """
        task.co_channels.add_co_pulse_chan_freq(device, freq=frequency, duty_cycle=duty_cycle, initial_delay=0.0)
        task.timing.cfg_implicit_timing(sample_mode=AcquisitionType.CONTINUOUS)
        task.start()

    def acquire_data_min_voltages(self, task, frequency, time_acquisition=None):
        """
        Acquiert les tensions minimales à partir de la tâche de mesure de tension.

        Paramètres :
        - task : Objet de tâche nidaqmx.
        - frequency : Fréquence de lecture de données (nombre d'acquisitions par seconde).
        - time_acquisition : Durée d'acquisition en secondes (facultatif).

        Retourne :
        - min_voltages : Liste des tensions minimales mesurées.

        """
        min_voltages = []
        start_time = time.time()
        while True:
            if time_acquisition and (time.time() - start_time >= time_acquisition):
                break
            data = task.read(number_of_samples_per_channel=self.samples_per_channel)
            min_voltages.append(np.min(data))
            if not time_acquisition and len(min_voltages) >= frequency:
                break
        return min_voltages

    def perform_voltage_acquisition(self, task_type, frequency, duty_cycle, channel, time_acquisition=None):
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
            if task_type in ['scanning', 'chemical_kinetics']:
                self.configure_task_impulsion(task_impulsion, frequency, duty_cycle)
            self.configure_task_voltage(task_voltage, self.channels[channel])
            min_voltages = self.acquire_data_min_voltages(task_voltage, frequency, time_acquisition)
            if task_type in ['scanning', 'chemical_kinetics']:
                task_impulsion.stop()
        return np.mean(min_voltages)

# Utilisation de la classe
#channels = ['Dev1/ai0', 'Dev1/ai1']
#acquisition = VoltageAcquisition(channels, sample_rate, samples_per_channel)
#mean_voltage = acquisition.perform_voltage_acquisition(task_type, frequency, duty_cycle, channel, time_acquisition)




