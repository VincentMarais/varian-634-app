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
    def __init__(self):
        """
        Initialise une instance de la classe VoltageAcquisition.

        Paramètres :
        - channels : Liste des canaux d'acquisition (par exemple, ['Dev1/ai0', 'Dev1/ai1']).
        - sample_rate : Taux d'échantillonnage en échantillons par seconde (Hz).
        - samples_per_channel : Nombre d'échantillons à acquérir par canal.

        """
        self.channels = ['Dev1/ai0', 'Dev1/ai1']  
        self.sample_rate = 30000
        self.samples_per_channel = 250000
        self.frequency = np.array([20.0])
        self.duty_cycle = np.array([0.5])
        self.counter='/Dev1/ctr0'

    def generate_pulse_task(self):
        # Créer une tâche pour générer un train d'impulsions
        with nidaqmx.Task() as pulse_task:
            pulse_task.co_channels.add_co_pulse_chan_freq(
                counter=self.counter,
                freq=self.frequency[0],
                duty_cycle=self.duty_cycle[0]
            )

            # On commence la tâche de génération d'impulsions
            pulse_task.start()

            # Attendre un certain temps (par exemple, 5 secondes)
            time.sleep(5)

            # Arrêter la tâche de génération d'impulsions
            pulse_task.stop()


    def initialisation_read_voltage_task(self, task):        
            task.ai_channels.add_ai_voltage_chan('Dev1/ai0')  # Remplacez par le nom de votre canal analogique

            # Configurer la tâche de lecture pour être déclenchée par le front montant
            # de l'impulsion générée sur le compteur (Dev1/ctr0).
            task.triggers.start_trigger.cfg_dig_edge_start_trig(
                trigger_source='Dev1/ctr0',  # Remplacez par le nom de votre compteur
                trigger_edge=nidaqmx.constants.Edge.RISING
            )
        
    def read_voltage_task(self):    
    # Créer une tâche pour lire la tension sur le canal 'ai0'
        with nidaqmx.Task() as read_task:
            self.initialisation_read_voltage_task(read_task)

            # Définir le nombre d'impulsions que vous souhaitez lire
            
            nombre_impulsions = int(self.frequency[0])
            compteur_impulsions = 0
            voltages=[]
            # Lire la tension à chaque front montant de l'impulsion
            while compteur_impulsions < nombre_impulsions:
                try:
                    voltage=read_task.read()
                    voltages.append(read_task.read())
                    print(f"Tension lue : {voltage} V")
                    compteur_impulsions += 1

                except nidaqmx.errors.DaqError as e:
                    # Gérer l'erreur si le compteur est arrêté (impulsions terminées)
                    if "The specified counter has been stopped" in str(e):
                        break
                    else:
                        raise
            return voltages

    def measure_routine(self):
        self.generate_pulse_task()
        y=self.read_voltage_task()
        return y
    
if __name__ == "__main__":
    # Faire un test avec un signal créneau
    ni_pci_6621=VoltageAcquisition()
    print(ni_pci_6621.measure_routine())
