# Test ni_pci_6621.py

```
Frequence_creneau = 20.0
Rapport_cyclique = 0.5
SAMPLES_PER_CHANNEL = 30000
SAMPLE_RATE = 250000
CHANNELS = ['Dev1/ai0', 'Dev1/ai1']  
NUM_ACQUISITIONS = 10  # Remplacez ceci par le nombre d'acquisitions que vous souhaitez effectuer

print(voltage_acquisition(samples_per_channel=SAMPLES_PER_CHANNEL, sample_rate=SAMPLE_RATE, 
                    square_wave_frequency=Frequence_creneau, duty_cycle=Rapport_cyclique, channels=CHANNELS, channel='ai0'))

```