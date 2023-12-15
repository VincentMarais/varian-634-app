# Test ni_pci_6621.py

```
Frequence_creneau = np.array([20.0])
Rapport_cyclique = np.array([0.5])
SAMPLES_PER_CHANNEL = 30000
SAMPLE_RATE = 250000
CHANNELS = ['Dev1/ai0', 'Dev1/ai1']  

print(voltage_acquisition_scanning(samples_per_channel=SAMPLES_PER_CHANNEL, sample_rate=SAMPLE_RATE, 
                    square_wave_frequency=Frequence_creneau, duty_cycle=Rapport_cyclique, channels=CHANNELS, channel='ai0'))
print(voltage_acquisition_baseline(samples_per_channel=SAMPLES_PER_CHANNEL, sample_rate=SAMPLE_RATE, 
                    square_wave_frequency=Frequence_creneau, channels=CHANNELS, channel='ai0'))

```