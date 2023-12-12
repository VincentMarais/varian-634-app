"""
This program allows reading the voltage across the photodiodes using an NI-PCI 6221 card.
Doc NI-PCI 6221
https://www.ni.com/docs/fr-FR/bundle/pci-pxi-usb-6221-specs/page/specs.html

"""

import numpy as np
import nidaqmx
from nidaqmx.constants import AcquisitionType, TerminalConfiguration

# Function acquisition_tension

def get_solution_cuvette():
    """
    Demande à l'utilisateur dans quelle cuve il a mis la référence
    """
    solution = input("Dans quelle cuve numéro est la solution blanche : cuve 1 ou cuve 2 : ")
    while solution not in ['cuve 1', 'cuve 2']:
        solution = input("Veuillez choisir cuve 1 ou cuve 2 : ")
    print("La solution de blanc est dans la", solution)
    return solution

def task_ni_pci(samples_per_channel, sample_rate,
                square_wave_frequency, duty_cycle, channels, min_voltages):
    """
    Fonction qui pilote la lampe à arc aux xénon en générant un signal créneau 
    et qui récupère les tensions aux bornes des photodiodes
    """
    with nidaqmx.Task() as task_impulsion, nidaqmx.Task() as task_voltage:
        task_impulsion.co_channels.add_co_pulse_chan_freq('/Dev1/ctr0',
            freq=square_wave_frequency[0], duty_cycle=duty_cycle[0], initial_delay=0.0)
        task_impulsion.timing.cfg_implicit_timing(sample_mode=AcquisitionType.CONTINUOUS)

        print(f"Génération du train d'impulsions avec une fréquence de {square_wave_frequency[0]} Hz et un rapport cyclique de {duty_cycle[0]}")
        task_impulsion.start()

        task_voltage.ai_channels.add_ai_voltage_chan(channels, terminal_config=TerminalConfiguration.DIFF)
        task_voltage.timing.cfg_samp_clk_timing(sample_rate, samps_per_chan=samples_per_channel, sample_mode=AcquisitionType.FINITE)
        frequency = int(square_wave_frequency[0])
        for _ in range(frequency):
            # Acquisition des données
            data = task_voltage.read(number_of_samples_per_channel=samples_per_channel)
            # Conversion des données en un tableau numpy pour faciliter les calculs
            np_data = np.array(data)
            # Trouver et stocker le minimum
            min_voltage = np.min(np_data)
            min_voltages.append(min_voltage)
        task_impulsion.stop()
        task_voltage.stop()
        mean = np.mean(min_voltages)
    return mean

def voltage_acquisition(samples_per_channel, sample_rate,
                        square_wave_frequency, duty_cycle, channels, channel):
    """
    Renvois la valeur de la tension entre du channel 'ai0' ou 'ai1' 
    (il faut que je développe ce commentaire avec la doc NI-PCI 6221)
    """
    min_voltages = []
    if channel == 'ai0': # Acquisition sur le 1er capteur
        mean = task_ni_pci(samples_per_channel, sample_rate, square_wave_frequency, duty_cycle, channels[0], min_voltages)
        return mean

    elif channel == 'ai1': # Acquisition sur le 2ème capteur
        mean = task_ni_pci(samples_per_channel, sample_rate, square_wave_frequency, duty_cycle, channels[1], min_voltages)
        return mean
# End-of-file (EOF)