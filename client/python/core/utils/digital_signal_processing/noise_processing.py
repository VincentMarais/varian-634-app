"""
This program will reduce the noise from the photodiode"""
import numpy as np
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt

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


    def voltage_possessing(self, door_function_width, voltage):
        """
        This program will perform voltage denoising (cf Report 2022-2023 for the professor).

        Entry: door_function_width 35 # optimal settings (Slit 0.2mm): 23 /
                (Slit 0.5mm): 30 / (Slit 1mm): 15 / (Slit 2mm): 30 (# Define the smoothing window size)
        voltage (list)  
        """
        voltage = np.convolve(voltage, np.ones(door_function_width) / door_function_width, mode='same')
        return voltage

    def spline_interpolation(self, datas_x, datas_y, title_datas_x, title_datas_y):
        """
        Entrée : 
            - data_y_spline (liste) : data_y calculer après lui avoir appliqué un spline cubique

        Sortie: data_y_spline (liste) : data_y calculer après lui avoir appliqué un spline cubique corrigé, c'est à dire :

                                                Pour tout i, data_y_spline[i] >= 0       

        BUT : Supprimer les data_y négative pour être en accord avec la réalité physique de notre solution 
        (cf Rapport 2022-2023 pour plus de détaille sur la physique du problème)        
        """
        spline = UnivariateSpline(datas_x, datas_y, s=20)
        datas_y_spline = spline(datas_x)
        for data_spline in datas_y_spline:
            if data_spline == max(data_spline, 0):
                data_spline = 0
        plt.figure()
        plt.plot(datas_x, datas_y, '-', label='Données bruitées')
        plt.plot(datas_x, datas_y_spline, '--', label='data interpolate cubic spline')
        plt.legend()
        plt.xlabel(title_datas_x)
        plt.ylabel(title_datas_y)
        plt.show()
        return datas_y_spline

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
