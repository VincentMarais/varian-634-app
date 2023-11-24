import numpy as np
import nidaqmx
from nidaqmx.constants import AcquisitionType, TerminalConfiguration



# Fonction acquisition_tension



def get_solution_cuvette():
    solution = input("Dans quelle cuve numéro est la solution blanche : cuve 1 ou cuve 2 : ")
    while solution not in ['cuve 1', 'cuve 2']:
        solution = input("Veuillez choisir cuve 1 ou cuve 2 : ")
    print("La solution de blanc est dans la", solution)
    return solution


def task_NI_PCI(SAMPLES_PER_CHANNEL, SAMPLE_RATE, square_wave_frequency, duty_cycle, CHANNELS, min_voltages):
    with nidaqmx.Task() as task_impulsion , nidaqmx.Task() as task_voltage :
            task_impulsion.co_channels.add_co_pulse_chan_freq('/Dev1/ctr0', freq=square_wave_frequency[0], duty_cycle=duty_cycle[0], initial_delay=0.0) # freq 1D numy et duty_cycle 1D numpy cf docs
            task_impulsion.timing.cfg_implicit_timing(sample_mode=AcquisitionType.CONTINUOUS)

            print(f"Génération du train d'impulsions avec une fréquence de {square_wave_frequency[0]} Hz et un rapport cyclique de {duty_cycle[0]}")
            task_impulsion.start()

                # Ici, vous pouvez insérer une pause ou attendre un certain événement avant de passer à la génération suivante
            task_voltage.ai_channels.add_ai_voltage_chan(CHANNELS, terminal_config=TerminalConfiguration.DIFF)
            
            task_voltage.timing.cfg_samp_clk_timing(SAMPLE_RATE, samps_per_chan=SAMPLES_PER_CHANNEL, sample_mode=AcquisitionType.FINITE)
            frequence = int(square_wave_frequency)
            for _ in range(frequence):
                # Acquisition des données
                    data = task_voltage.read(number_of_samples_per_channel=SAMPLES_PER_CHANNEL)
                # Conversion des données en un tableau numpy pour faciliter les calculs
                    np_data = np.array(data)
                
                # Trouver et stocker le minimum
                    min_voltage = np.min(np_data)
                    min_voltages.append(min_voltage)
            task_impulsion.stop()
            task_voltage.stop()
            mean=np.mean(min_voltages)
    return mean



def voltage_acquisition(SAMPLES_PER_CHANNEL, SAMPLE_RATE, square_wave_frequency, duty_cycle, CHANNELS, channel):
    min_voltages = []
    
    if channel=='ai0': # Acquisition sur le 1er capteur
        mean=task_NI_PCI(SAMPLES_PER_CHANNEL, SAMPLE_RATE, square_wave_frequency, duty_cycle, CHANNELS[0], min_voltages)        
        return mean


    elif  channel=='ai1': # Acquisition sur le 2eme capteur
        mean=task_NI_PCI(SAMPLES_PER_CHANNEL, SAMPLE_RATE, square_wave_frequency, duty_cycle, CHANNELS[1], min_voltages)

        return mean


