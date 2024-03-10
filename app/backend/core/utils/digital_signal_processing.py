"""
This program will reduce the noise from the photodiode
"""

import numpy as np
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt
import pandas as pd
from scipy.signal import hilbert, savgol_filter
from scipy.signal import find_peaks
from scipy.sparse.linalg import spsolve
from scipy import sparse
from pybaselines import Baseline



class PhotodiodeNoiseReducer:
    """
    A class to reduce noise from photodiode signals.

    ...

    Methods
    -------
    negative_absorbance_correction(voltages_sample_reference, voltage_sample_analyzed):
        Corrects the analyzed sample voltages based on reference sample voltages.

    graph_digital_processing(data_x, datas_y, title_graph, titles_data_y):
        Plots a digital signal processing graph.

    fourier_transform(signal):
        Performs Fourier transform on the input signal and displays the temporal and frequency domains.

    hilbert_transform(signal):
        Applies Hilbert transform to the input signal and plots the original signal and envelope.

    simulation_gaussian_noise():
        Simulates a signal with Gaussian noise and performs Fourier transform on it.

    spline_interpolation(signal, smoothing_factor):
        Applies cubic spline interpolation to the input signal and plots the original and interpolated signals.

    sample_absorbance(absorbance_baseline, absorbance_scanning):
        Reduces the difference between two photodiode signals.

    voltage_possessing(door_function_width, voltage):
        Performs voltage denoising using convolution with a smoothing window.

    """

    def __init__(self):
        pass

    def negative_absorbance_correction(self, voltages_sample_reference, voltage_sample_analyzed):
        """
        Corrects the analyzed sample voltages based on reference sample voltages.

        Parameters:
            voltages_sample_reference (list): List of voltages measured at the photodiode terminals with the blank solution.
            voltage_sample_analyzed (list): List of voltages measured at the photodiode terminals with the sample.

        Returns:
            tuple: Updated lists of voltages for reference sample and analyzed sample.
        """
        for i, (voltage_ref, voltage_analyzed) in enumerate(zip(voltages_sample_reference, voltage_sample_analyzed)):
            if np.abs(voltage_ref) < np.abs(voltage_analyzed):
                voltage_sample_analyzed[i] = voltage_ref
        return voltages_sample_reference, voltage_sample_analyzed


    def calculate_wavelength(self, position):
        """
        Calculates the wavelength based on the position.
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

    def simulation_gaussian_noise(self):
        """
        Simulates a signal with Gaussian noise and performs Fourier transform on it.

        Returns:
            None
        """
        amplitude = 1.0
        frequency = 5.0
        duration = 1.0
        num_samples = 3000

        time = np.linspace(0, duration, num_samples, endpoint=False)
        sinusoidal_signal = amplitude * np.sin(2 * np.pi * frequency * time)
        gaussian_noise = np.random.normal(0, 0.5, num_samples)
        signal = sinusoidal_signal + gaussian_noise

        plt.figure(figsize=(12, 4))
        plt.plot(time, sinusoidal_signal, label='Sinusoidal Signal')
        plt.plot(time, signal, label='Signal with Noise')
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.show()
        self.fourier_transform(signal)
        self.fourier_transform(sinusoidal_signal)

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

    def sample_absorbance(self, absorbance_baseline, absorbance_scanning):
        """
        Reduces the difference between two photodiode signals. Because 
        theoretically the absorbance A=0 with no cuvettes but is not 
        true because two photodiodes is differente

        Parameters:
            absorbance_baseline (array): Baseline absorbance signal.
            absorbance_scanning (array): Scanning absorbance signal.

        Returns:
            array: Sample absorbance signal.
        """
        absorbance_baseline_mean = np.mean(absorbance_baseline)
        sample_absorbance = [absorbance_scanning[i] - absorbance_baseline_mean for i in range(len(absorbance_scanning))]
        return sample_absorbance

    def voltage_possessing(self, door_function_width, voltage):
        """
        Performs voltage denoising using convolution with a smoothing window.

        Parameters:
            door_function_width (int): Smoothing window size.
            voltage (array): Input voltage signal.

        Returns:
            array: Denoised voltage signal.
        """
        voltage_convol = np.convolve(voltage, np.ones(door_function_width) / door_function_width, mode='same')
        return voltage_convol
    
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
    
    def aals(self, x, y, alpha=0.01, beta=0.01, tol=1e-5, max_iter=1000):
        """
        Adaptive Asymmetric Least Squares baseline estimation.

        Parameters:
        x (array_like): The independent variable (e.g. wavelength).
        y (array_like): The dependent variable (e.g. signal).
        alpha (float): The asymmetry parameter for the LS fit.
        beta (float): The smoothing parameter for the running average.
        tol (float): The tolerance for convergence.
        max_iter (int): The maximum number of iterations.

        Returns:
        (array_like) The estimated baseline.
        """
        n = len(x)
        y_hat = np.zeros_like(y)
        resid = np.zeros_like(y)

        # Initialize running average
        window = int(n * beta)
        if window % 2 == 0:
            window += 1
        ma = np.convolve(y, np.ones(window) / window, mode='same')

        for i in range(max_iter):
            # Compute residuals
            y_hat[:-1] = ma[:-1] + alpha * (y[1:] - ma[:-1])
            resid[:-1] = y[:-1] - y_hat[:-1]

            # Update running average
            ma = np.convolve(resid, np.ones(window) / window, mode='same')

            # Check for convergence
            if np.max(np.abs(resid[1:] - resid[:-1])) < tol:
                break


        return y_hat
    


    def als(self, y, lam=1e6, p=0.1, itermax=10):
        """
        Implements an Asymmetric Least Squares Smoothing
        baseline correction algorithm (P. Eilers, H. Boelens 2005)

        Baseline Correction with Asymmetric Least Squares Smoothing
        based on https://github.com/vicngtor/BaySpecPlots

        Baseline Correction with Asymmetric Least Squares Smoothing
        Paul H. C. Eilers and Hans F.M. Boelens
        October 21, 2005

        Description from the original documentation:

        Most baseline problems in instrumental methods are characterized by a smooth
        baseline and a superimposed signal that carries the analytical information: a series
        of peaks that are either all positive or all negative. We combine a smoother
        with asymmetric weighting of deviations from the (smooth) trend get an effective
        baseline estimator. It is easy to use, fast and keeps the analytical peak signal intact.
        No prior information about peak shapes or baseline (polynomial) is needed
        by the method. The performance is illustrated by simulation and applications to
        real data.


        Inputs:
            y:
                input data (i.e. chromatogram of spectrum)
            lam:
                parameter that can be adjusted by user. The larger lambda is,
                the smoother the resulting background, z
            p:
                wheighting deviations. 0.5 = symmetric, <0.5: negative
                deviations are stronger suppressed
            itermax:
                number of iterations to perform
        Output:
            the fitted background vector

        """
        L = len(y)
    #  D = sparse.csc_matrix(np.diff(np.eye(L), 2))
        D = sparse.eye(L, format='csc')
        D = D[1:] - D[:-1]  # numpy.diff( ,2) does not work with sparse matrix. This is a workaround.
        D = D[1:] - D[:-1]
        D = D.T
        w = np.ones(L)
        for i in range(itermax):
            W = sparse.diags(w, 0, shape=(L, L))
            Z = W + lam * D.dot(D.T)
            z = spsolve(Z, w * y)
            w = p * (y > z) + (1 - p) * (y < z)
        return z
    

    
    
    def correction_baseline(self, wavelength, absorbance):
        """
        Corrige le gap en les deux photodiode, 
        nous avons remarqué quand trançant le spectre du Xe sur les 
        des photodiodes la Tension photodiode 1  = Tension phodiode_2 + a

        Ce programme permet de déterminer a, afin d'avoir 
        Tension photodiode 1  = Tension phodiode_2
        et donc Absorbance_baseline = 0
        """
        absorbance_baseline = self.aals(wavelength, absorbance)
        
        absorbance_fit = savgol_filter(absorbance_baseline, window_length=15, polyorder=2, deriv=0, delta=0.01)

        return absorbance_fit


    def adjust_absorbance(self, wavelength, absorbance):
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


if __name__ == "__main__":
    denoise = PhotodiodeNoiseReducer()

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
    voltage_1 = data["Tension photodiode 1 (Volt)"]
    voltage_2 = data["Tension photodiode 2 (Volt)"]
    screw = data["pas de vis (mm)"]
    WAVELENGTH = np.array([denoise.calculate_wavelength(p) for p in screw])
    absorbance_no_baseline = np.log10(np.array(voltage_1)/np.array(voltage_2))
  

        # Seuil de hauteur pour la détection des pics
    hauteur_seuil = 0.1
    y = denoise.adjust_absorbance(WAVELENGTH, absorbance_no_baseline)
    # Trouver les indices et les propriétés des pics
    indices_pics, proprietes_pics = find_peaks(y, height=hauteur_seuil)

    # Extraire les hauteurs des pics
    hauteurs_pics = proprietes_pics['peak_heights']
    print("WAVELENGTH[indices_pics]", WAVELENGTH[indices_pics])
    # Afficher le signal et les pics détectés
  

    plt.plot(WAVELENGTH, absorbance_no_baseline, label='Absorbance bromophénol sans ligne de base')    
    plt.plot(WAVELENGTH, y , label='Absorbance bromophénol aspls')
    plt.axhline(y=hauteur_seuil, color='r', linestyle='--', label='Seuil de hauteur')
    plt.scatter(WAVELENGTH[indices_pics], y[indices_pics], label='Pics détectés', color='red')
    # Annoter chaque pic avec ses coordonnées
    for i, txt in enumerate(indices_pics):
        plt.text(WAVELENGTH[txt], y[txt], f'({WAVELENGTH[txt]:.2f}, {y[txt]:.2f})', fontsize=8)
    plt.legend()
    plt.show()
    absorb = denoise.correction_baseline(WAVELENGTH,absorbance_no_baseline)
    peaks, _ = find_peaks(absorb, prominence=0)

    

    # Convertir les indices des pics en un array python
    peak_values = np.array([absorb[i] for i in peaks])
    print(peak_values)