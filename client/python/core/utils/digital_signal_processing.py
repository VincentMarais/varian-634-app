"""
This program will reduce the noise from the photodiode
"""

import numpy as np
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt
import pandas as pd
from scipy.signal import hilbert


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
        plt.legend()
        plt.xlabel("x")
        plt.ylabel("y")
        plt.title(title_graph)
        plt.grid()

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

    def spline_interpolation(self, signal, smoothing_factor):
        """
        Applies cubic spline interpolation to the input signal and plots the original and interpolated signals.

        Parameters:
            signal (array): Input signal.
            smoothing_factor (float): Smoothing factor for spline interpolation.

        Returns:
            array: Interpolated signal.
        """
        x_data = np.arange(0, len(signal), 1)
        spline = UnivariateSpline(x_data, signal, s=smoothing_factor)
        signal_spline = spline(x_data)
        y_datas = [signal, signal_spline]
        title_datas_y = ['Noisy Signal', 'Interpolated Cubic Spline Data']
        self.graph_digital_processing(x_data, y_datas, 'Spline', title_datas_y)
        return signal_spline

    def sample_absorbance(self, absorbance_baseline, absorbance_scanning):
        """
        Reduces the difference between two photodiode signals.

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


if __name__ == "__main__":
    denoise = PhotodiodeNoiseReducer()
    CHEMIN = "C:\\Users\\admin\\Documents\\Projet_GP\\Programmation_Spectro\\Programmation_application_spectro\\Manip\\Manip_2023\\Manip_06_2023\\28_06_2023\\Fente_0_2nm"

    FILE_REF_SAMPLE = CHEMIN + '\\' + "Tension_de_blanc_28_06_2023_Fente_0_2nm.csv"
    FILE_SAMPLE = CHEMIN + '\\' + "Tension_de_echantillon_28_06_2023_Fente_0_2nm.csv"

    data_ref_sample = pd.read_csv(FILE_REF_SAMPLE, encoding='ISO-8859-1')
    data_sample = pd.read_csv(FILE_SAMPLE, encoding='ISO-8859-1')

    # Extract columns
    wavelength = data_ref_sample['Longueur d\'onde (nm)']
    voltages_ref_sample = data_ref_sample['Tension blanc (Volt)']
    voltages_sample = data_sample['Tension échantillon (Volt)']
    denoise.fourier_transform(voltages_sample)
    denoise.hilbert_transform(voltages_sample)
    denoise.spline_interpolation(voltages_sample, 0.5)
    denoise.simulation_gaussian_noise()
