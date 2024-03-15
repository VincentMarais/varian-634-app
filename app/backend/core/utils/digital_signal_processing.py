"""
This program will reduce the noise from the photodiode
"""

import numpy as np
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt
import pandas as pd
from scipy.signal import hilbert, savgol_filter, find_peaks
from pybaselines import Baseline



class SignalProcessingVarian634:
    """
    A class to reduce noise from photodiode signals. 

    """

    def __init__(self):
        pass

# Tools Signal processing
    def calculate_wavelength(self, position):
        """
        Calculates the wavelength based on the position.
        Formule déterminé grâce au calibrage
        """
        return -32.02 * position + 886.13
    
    def calculate_course(self, wavelength):
        """
        Calculates the wavelength based on the position.
        abs pour que GBRL est des valeurs positive de position cela 
        évite l'initialisé dans le sens inverse
        """
        return np.abs((wavelength - 886.13)/-32.02)

    def graph_digital_processing(self, data_x, datas_y, title_graph, titles_data_y):
        """
        Plots a digital signal processing graph.

        Parameters:
            data_x (array): x-axis data.
            datas_y (list): List of y-axis data arrays.
            title_graph (str): Title of the graph.
            titles_data_y (list): List of y-axis data titles.

        Returns:
            None
        """
        plt.figure()
        for data_y, title_data_y in zip(datas_y, titles_data_y):
            plt.plot(data_x, data_y, '-', label=title_data_y)
        plt.xlabel("x")
        plt.ylabel("y")
        plt.title(title_graph)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()


# Mathematical tools
        
    def best_polyfit(self, x, y):
        best_r2 = -np.inf
        best_coefficients = None
        x = np.array(x)
        y = np.array(y)
        
        for degree in range(3):
            coefficients = np.polyfit(x, y, degree)
            # Ensure coefficients are array-like
            coefficients = np.atleast_1d(coefficients)
            
            fitted_values = np.polyval(coefficients, x)
            residuals = y - fitted_values
            ss_res = np.sum(residuals ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            
            # Handle case where ss_tot is zero
            if ss_tot == 0:
                r2 = float('nan')  # or some other value indicating an undefined R^2
            else:
                r2 = 1 - (ss_res / ss_tot)
            
            if r2 > best_r2:
                best_r2 = r2
                best_coefficients = coefficients
        
        return best_coefficients
    
    def fourier_transform(self, signal):
        """
        Performs Fourier transform on the input signal and displays the temporal and frequency domains.

        Parameters:
            signal (array): Input signal.

        Returns:
            None
        """
        t = np.arange(0, 1, 1 / len(signal))  # Time from 0 to 1 second with a step of 1/fs

        fft_result = np.fft.fft(a=signal, n=len(signal), norm='forward')
        fft_freqs = np.fft.fftfreq(len(fft_result), 1 / len(signal))
        positive_freqs = fft_freqs[:len(fft_result) // 2]
        magnitude_spectrum = np.abs(fft_result[:len(fft_result) // 2])

        threshold = np.max(magnitude_spectrum) / 2
        peaks = positive_freqs[magnitude_spectrum > threshold]

        plt.figure(figsize=(10, 6))
        plt.subplot(2, 1, 1)
        plt.plot(t, signal)
        plt.title('Temporal Signal')
        plt.grid()
        plt.tight_layout()
        plt.subplot(2, 1, 2)
        plt.plot(positive_freqs, magnitude_spectrum)
        plt.scatter(peaks, magnitude_spectrum[magnitude_spectrum > threshold], color='red', label='Detected Peak')
        plt.title('Fourier Transform of the Signal')
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.show()

    def hilbert_transform(self, signal):
        """
        Applies Hilbert transform to the input signal and plots the original signal and envelope.

        Parameters:
            signal (array): Input signal.

        Returns:
            None
        """
        analytic_signal = hilbert(signal)
        amplitude_envelope = np.abs(analytic_signal)
        x_datas = np.arange(0, len(signal), 1)
        y_datas = [signal, amplitude_envelope]
        titles_data_y = ['Signal', 'Hilbert Transform']
        self.graph_digital_processing(x_datas, y_datas, 'Hilbert', titles_data_y)
        plt.show()

    def spline_interpolation(self, x_data, signal, smoothing_factor):
        """
        Applies cubic spline interpolation to the input signal and plots the original and interpolated signals.

        Parameters:
            signal (array): Input signal.
            smoothing_factor (float): Smoothing factor for spline interpolation.

        Returns:
            array: Interpolated signal.
        """
        spline_test = UnivariateSpline(x_data, signal, s=smoothing_factor)
        signal_spline = spline_test(x_data)
        y_datas = [signal, signal_spline]
        title_datas_y = ['Noisy Signal', 'Interpolated Cubic Spline Data']
        self.graph_digital_processing(x_data, y_datas, 'Spline', title_datas_y)
        return signal_spline

    
    def calculate_average_translation(self, list_A, list_B):
        """
        Corrige le gap en les deux photodiode, 
        nous avons remarqué quand trançant le spectre du Xe sur les 
        des photodiodes la Tension photodiode 1  = Tension phodiode_2 + a

        Ce programme permet de déterminer a, afin d'avoir 
        Tension photodiode 1  = Tension phodiode_2
        et donc Absorbance_baseline = 0
        """
        # Check if both lists are of the same size
        if len(list_A) != len(list_B):
            raise ValueError("Both lists must be of the same size.")
        
        # Initialize the sums of differences in x and y
        sum_diff_x = 0
        
        # Calculate the sum of differences between corresponding points
        for x_a, x_b in zip(list_A, list_B):
            sum_diff_x += x_a - x_b
        
        # Calculate the averages
        n = len(list_A)  # Number of points
        average_x = sum_diff_x / n
        
        return average_x    

    
# Baseline correction
    def baseline_correction_aspls(self, wavelength, absorbance):
        """
        Ajuste les valeurs d'absorbance en fonction de la baseline.
        
        Parameters:
        - absorbance (list): Une liste d'absorbance correspondante.
        
        Returns:
        - list: La liste d'absorbance ajustée.
        """
        # Vérifie si baseline et absorbance ont la même longueur
        
        baseline_fitter = Baseline(wavelength, check_finite=False)
        baseline = baseline_fitter.aspls(list(absorbance), 1e6)[0]
        if len(baseline) != len(absorbance):
            raise ValueError("baseline et absorbance doivent avoir la même longueur")
        
        # Ajuste l'absorbance en fonction de la valeur de baseline
        adjusted_absorbance = []
        for base, abs_val in zip(baseline, absorbance):            
                adjusted_absorbance.append(abs_val - base)
            
        absorbance_fit = savgol_filter(adjusted_absorbance, window_length=11, polyorder=2, deriv=0, delta=0.01)

        return absorbance_fit
    

    def baseline_correction_polyfit(self, wavelength_baseline, absorbance_baseline, wavelenght, absorbance):
        """
        
        """
        wavelenght_baseline = np.array(wavelength_baseline)
        absorbance_baseline = np.array(absorbance_baseline)
        wavelenght = np.array(wavelenght)
        absorbance = np.array(absorbance)
        coefficients = self.best_polyfit(wavelenght_baseline, absorbance_baseline)
        baseline = np.polyval(coefficients, wavelenght)
        adjusted_absorbance = []
        for base, abs_val in zip(baseline, absorbance):            
                adjusted_absorbance.append(abs_val - base)

        absorbance_fit = savgol_filter(adjusted_absorbance, window_length=15, polyorder=2, deriv=0, delta=0.01)
        return absorbance_fit




if __name__ == "__main__":
    signal_processing = SignalProcessingVarian634()

    import tkinter as tk
    from tkinter import filedialog

    def file_path():
        # Créer une instance de Tk
        root = tk.Tk()
        # Cacher la fenêtre principale de Tk
        root.withdraw()

        # Ouvrir la fenêtre de dialogue pour choisir un fichier
        file_selected = filedialog.askopenfilename()

        print(file_selected)
        
        return file_selected

    file = file_path()

    print("Absorbance baseline et non baseline")



    data = pd.read_csv(file, encoding='ISO-8859-1')
    
    voltage_ref = data["Tension reference (Volt)"]
    voltage_sample = data["Tension echantillon (Volt)"]
    screw = data["pas de vis (mm)"]
    WAVELENGTH = np.array([signal_processing.calculate_wavelength(p+ 7.062148657089319)  for p in screw]) 
    absorbance_no_baseline = np.log10(np.array(voltage_ref)/np.array(voltage_sample))
    print(WAVELENGTH)

    file_baseline = "C:\\Users\\admin\\Desktop\\GitHub\\varian-634-app\\experiments\\experiments_2024\\experiments_02_2024\\experiments_23_02_2024\\calibrage\\calibrage_23_02_2024_fente_2nm.csv" 
    data_baseline = pd.read_csv(file_baseline, encoding='ISO-8859-1')
    voltage_1_base = data_baseline["Tension photodiode 1 (Volt)"]
    voltage_2_base = data_baseline["Tension photodiode 2 (Volt)"]
    ABSORBANCE_BASELINE = np.log10(np.array(voltage_2_base)/np.array(voltage_1_base))
    screw = data_baseline["pas de vis (mm)"]
    WAVELENGTH_BASELINE = np.array([signal_processing.calculate_wavelength(p)  for p in screw]) 
    absor_fit = signal_processing.baseline_correction_polyfit(WAVELENGTH_BASELINE, ABSORBANCE_BASELINE, WAVELENGTH, absorbance_no_baseline)

        # Seuil de hauteur pour la détection des pics
    hauteur_seuil = 0.1
    y = signal_processing.baseline_correction_aspls(WAVELENGTH, absorbance_no_baseline)
    hauteur_seuil = 1
    absor_fit = signal_processing.baseline_correction_polyfit(WAVELENGTH_BASELINE, ABSORBANCE_BASELINE, WAVELENGTH, absorbance_no_baseline)
    # Trouver les indices et les propriétés des pics
    indices_pics, proprietes_pics = find_peaks(y, height=hauteur_seuil)
    indices_pics_absorb, proprietes_pics_absor = find_peaks(absor_fit, height=hauteur_seuil)

    # Extraire les hauteurs des pics
    hauteurs_pics = proprietes_pics['peak_heights']
    hauteurs_pics_absor = proprietes_pics['peak_heights']


    # Afficher le signal et les pics détectés
    absorbance_peak = max(absor_fit)
    wavelength_peak = WAVELENGTH[np.argmax((absor_fit))]

    indices_pics = np.asarray(indices_pics, dtype=int)
    y_a = savgol_filter(absorbance_no_baseline, window_length=11, polyorder=2, deriv=0, delta=0.01)
    plt.plot(WAVELENGTH, absorbance_no_baseline, label='Absorbance bromophénol sans ligne de base')    
    plt.plot(WAVELENGTH, y , label='Absorbance bromophénol aspls')
    plt.plot(WAVELENGTH, absor_fit, label='Absorbance bromophénol fit polyfit')
    plt.axhline(y=hauteur_seuil, color='r', linestyle='--', label='Seuil de hauteur')
    plt.scatter(WAVELENGTH[indices_pics], y[indices_pics], label='Pics détectés', color='red')
    plt.scatter(WAVELENGTH[indices_pics], y_a[indices_pics], label='Pics détectés lissé')
    

    # Annoter chaque pic avec ses coordonnées
    for txt_index in indices_pics:
        plt.text(WAVELENGTH[txt_index], y[txt_index], f'({WAVELENGTH[txt_index]:.2f}, {y[txt_index]:.2f})', fontsize=8)
    plt.scatter(wavelength_peak, absorbance_peak, color='red')

    plt.annotate(f'({wavelength_peak:.2f} nm, {absorbance_peak:.2f})',
                     xy=(wavelength_peak, absorbance_peak),
                     xytext=(wavelength_peak -30, absorbance_peak),
                     fontsize=10,
                     color='red',
                     arrowprops=dict(facecolor='red', arrowstyle='->'))
    plt.grid(True)
    plt.legend()
    plt.show()
    absorb = signal_processing.correction_baseline(WAVELENGTH,absorbance_no_baseline)
    peaks, _ = find_peaks(absorb, prominence=0)

    

    # Convertir les indices des pics en un array python
    peak_values = np.array([absorb[i] for i in peaks])
    print(peak_values)