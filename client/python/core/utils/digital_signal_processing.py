"""
This program will reduce the noise from the photodiode"""
import numpy as np
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt
import pandas as pd
from scipy.signal import hilbert

class PhotodiodeNoiseReducer:
    def __init__(self):
        pass

    def negative_absorbance_correction(self, voltages_sample_reference, voltage_sample_analyzed):
        """
        Entrée : 
            - voltages_sample_reference (liste) : Liste des tensions mesurer aux bornes de la photodiode où il y a la cuve de la solution de blanc.
            - voltage_sample_analyzed (liste) : Liste des tensions mesurer aux bornes de la photodiode où il y a la cuve de l'échantillon.
        
        Sortie :
            - voltages_sample_reference (liste) : Liste des tensions mesurer aux bornes de la photodiode où il y a la cuve de la solution de blanc.
            - voltage_sample_analyzed (liste) : Liste des tensions mesurer aux bornes de la photodiode où il y a la cuve de l'échantillon corrigé, 
            c'est à dire que pour toute voltage_sample_analyzed[i] et voltage_sample_reference[i] on a :
            voltage_sample_analyzed[i] =< voltage_sample_reference[i]
                
        BUT : Supprimer les absorbance négatives pour être en accord avec la réalité physique de notre solution 
        (cf Rapport 2022-2023 pour plus de détails sur la physique du problème)
        """
        for i, (voltage_ref, voltage_analyzed) in enumerate(zip(voltages_sample_reference, voltage_sample_analyzed)):
            if np.abs(voltage_ref) < np.abs(voltage_analyzed):
                voltage_sample_analyzed[i] = voltage_ref
        return voltages_sample_reference, voltage_sample_analyzed

    def graph_digital_processing(self, data_x , datas_y, title_graph, titles_data_y):
        plt.figure()
        for data_y, title_data_y in zip(datas_y, titles_data_y):
            plt.plot(data_x, data_y, '-', label=title_data_y)
        plt.legend()
        plt.xlabel("x")
        plt.ylabel("y")
        plt.title(title_graph)
        plt.show()

    def fourier_transform(self, signal):
        t = np.arange(0, 1, 1/len(signal))  # Temps de 0 à 1 seconde avec un pas de 1/fs

        # Calcul de la transformée de Fourier
        fft_result = np.fft.fft(signal)
        fft_freqs = np.fft.fftfreq(len(fft_result), 1/len(signal))

        # Extraction des composantes fréquentielles
        positive_freqs = fft_freqs[:len(fft_result)//2]
        magnitude_spectrum = np.abs(fft_result[:len(fft_result)//2])

        threshold=np.max(magnitude_spectrum)/2
        # Détection des pics
        peaks = positive_freqs[magnitude_spectrum > threshold]
        print("peaks",peaks)
        # Affichage du signal et des pics détectés
        plt.figure(figsize=(10, 6))
        plt.subplot(2, 1, 1)
        plt.plot(t, signal)
        plt.title('Signal temporel')
        plt.subplot(2, 1, 2)
        plt.plot(positive_freqs, magnitude_spectrum)
        plt.scatter(peaks, magnitude_spectrum[magnitude_spectrum > threshold], color='red', label='Pic détecté')
        plt.title('Transformée de Fourier du signal')
        plt.legend()
        plt.show()

    def hilbert_transform(self, signal):
        analytic_signal = hilbert(signal)
        amplitude_envelope = np.abs(signal)
        x_datas= np.arange(0, len(signal), 1)  # Temps de 0 à 1 seconde avec un pas de 1/fs
        y_datas=[analytic_signal, amplitude_envelope]
        titles_data_y=['signal', 'hilbert transform']
        self.graph_digital_processing(x_datas,y_datas, 'hilbert', titles_data_y)
        plt.show()

    def spline_interpolation(self, signal, smoothing_factor):
        """
        Entrée : 
            - data_y_spline (liste) : data_y calculer après lui avoir appliqué un spline cubique

        Sortie: data_y_spline (liste) : data_y calculer après lui avoir appliqué un spline cubique corrigé, c'est à dire :

                                                Pour tout i, data_y_spline[i] >= 0       

        BUT : Supprimer les data_y négative pour être en accord avec la réalité physique de notre solution 
        (cf Rapport 2022-2023 pour plus de détaille sur la physique du problème)        
        """
        x_data= np.arange(0, len(signal), 1)
        spline = UnivariateSpline(x_data, signal, s=smoothing_factor)
        signal_spline = spline(x_data)
        y_datas=[signal, signal_spline]
        title_datas_y=['Signal bruitées', 'data interpolate cubic spline']
        self.graph_digital_processing(x_data, y_datas, 'spline', title_datas_y)        
        return signal_spline

    def sample_absorbance(self, absorbance_baseline, absorbance_scanning, pas_scanning):
        """
        Reduce the difference betwenn too photodiode
        """
        absorbance_baseline_acquisition = []
        sample_absorbance = []
        for i in range(0, len(absorbance_baseline), pas_scanning):
            absorbance_baseline_acquisition.append(absorbance_baseline[i])
        for i in range(absorbance_scanning):
            diff = absorbance_scanning[i] - absorbance_baseline_acquisition[i]
            sample_absorbance.append(diff)
        return sample_absorbance

    def voltage_possessing(self, door_function_width, voltage):
        """
        This program will perform voltage denoising (cf Report 2022-2023 for the professor).

        Entry: door_function_width 35 # optimal settings (Slit 0.2mm): 23 /
                (Slit 0.5mm): 30 / (Slit 1mm): 15 / (Slit 2mm): 30 (# Define the smoothing window size)
        voltage (list)  
        """
        voltage = np.convolve(voltage, np.ones(door_function_width) / door_function_width, mode='same')
        return voltage

if __name__ == "__main__":
    denoise=PhotodiodeNoiseReducer()
    CHEMIN="C:\\Users\\admin\\Documents\\Projet_GP\\Programmation_Spectro\\Programmation_application_spectro\\Manip\\Manip_2023\\Manip_06_2023\\28_06_2023\\Fente_0_2nm"

    """
    Lecture des fichier csv créé lors de l'acquisition 
    """


    fichier_blanc=  CHEMIN + '\\'+ "Tension_de_blanc_28_06_2023_Fente_0_2nm.csv"
    fichier_echantillon=  CHEMIN + '\\' + "Tension_de_echantillon_28_06_2023_Fente_0_2nm.csv"

    data_solution_blanc = pd.read_csv(fichier_blanc, encoding='ISO-8859-1')
    data_solution_echantillon= pd.read_csv(fichier_echantillon, encoding='ISO-8859-1')

    # Obtenir les colonnes 
    Longueur_donde = data_solution_echantillon['Longueur d\'onde (nm)']
    Tension_blanc = data_solution_blanc['Tension blanc (Volt)']
    Tension_echantillon= data_solution_echantillon['Tension échantillon (Volt)']
    denoise.fourier_transform(Tension_echantillon)
    denoise.hilbert_transform(Tension_echantillon)
    denoise.spline_interpolation(Tension_echantillon, 0.5)

    
