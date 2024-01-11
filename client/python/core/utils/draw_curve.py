import matplotlib.pyplot as plt
import numpy as np
from utils.directory_creation import path_creation
from utils.data_csv import save_data_csv, csv_experiment
from scipy.signal import find_peaks 

class Varian634ExperimentPlotter:
    def __init__(self, path, sample_reference_file, sample_analyzed_file, title, FE):
        self.path= path
        self.sample_reference_file=sample_reference_file
        self.sample_analyzed_file= sample_analyzed_file
        self.title= title
        self.FE= FE

    def max_absorbance_display(self, wavelength_peak, absorbance_peak, wavelength, absorbance):
        plt.scatter(wavelength_peak, absorbance_peak, color='red')

        plt.annotate(f'({wavelength_peak:.2f} nm, {absorbance_peak:.2f})',
                     xy=(wavelength_peak, absorbance_peak),
                     xytext=(wavelength_peak + 10, absorbance_peak),
                     fontsize=10,
                     color='red',
                     arrowprops=dict(facecolor='red', arrowstyle='->'))

        plt.hlines(y=absorbance_peak, xmin=wavelength[0], xmax=wavelength_peak, linestyle='dashed', color='red')

        plt.vlines(x=wavelength_peak, ymin=min(absorbance), ymax=absorbance_peak, linestyle='dashed', color='red')

    def graph(self, sample_analyzed_name, graph_title, peak_search_window):
        [wavelength, voltage_sample_reference, voltage_sample_analyzed] = csv_experiment(path, sample_reference_file, sample_analyzed_file)

        absorbance = np.log10(np.abs(voltage_sample_reference) / np.abs(voltage_sample_analyzed))
        absorbance_peak = max(absorbance)
        wavelength_peak = wavelength[np.argmax((absorbance))]
        peaks, _ = find_peaks(absorbance, distance=peak_search_window)
        save_data_csv(path=path, file_name="peak" + graph_title, data_list=[peaks, wavelength[peaks]], title_list=["pic_absorbance", "longueur d'onde"])

        plt.plot(wavelength, absorbance)
        plt.plot(wavelength[peaks], absorbance[peaks], 'ro')

        plt.xlabel('Longueur d\'onde (nm)')
        plt.ylabel('Absorbance')
        plt.title('Absorbance du ' + sample_analyzed_name)
        self.max_absorbance_display(wavelength_peak, absorbance_peak, wavelength, absorbance)

        plt.savefig(path + '\\' + graph_title + ".pdf")
        plt.show()

    def voltage_curve_display(self):
        [wavelength, voltage_sample_reference, voltage_sample_analyzed] = csv_experiment(path, sample_reference_file, sample_analyzed_file)

        plt.plot(wavelength, voltage_sample_reference, color='red')
        plt.xlabel('Longueur d\'onde (nm)')
        plt.ylabel('Tension reference (Volt)')
        plt.title(title)
        path = path_creation(path, 'Tension reference')
        plt.savefig(path + "\\" + title + ".pdf")
        plt.show()

        plt.plot(wavelength, voltage_sample_analyzed, color='blue')
        plt.xlabel('Longueur d\'onde (nm)')
        plt.ylabel('Tension analyzed (Volt)')
        plt.title(title)
        path = path_creation(path, 'Tension analyzed')
        plt.savefig(path + "\\" + title + ".pdf")
        plt.show()

    def fourier_transformed_display(self, FE, sample_reference_file, sample_analyzed_file):
        [wavelength, voltage_sample_reference, voltage_sample_analyzed] = csv_experiment(path, sample_reference_file, sample_analyzed_file)

        fourier_transform = np.fft.fft(voltage_sample_reference, n=4096)
        f = FE * np.arange(4096) / 4096
        fourier_transform = np.abs(fourier_transform)
        plt.plot(f, fourier_transform, color='red')
        plt.xlabel('Fréquence (Hz)')
        plt.ylabel('Module de la transformée de Fourier')
        plt.title(title)
        path = path_creation(path, 'Transformee_de_Fourier')
        plt.savefig(path + "\\" + title + ".pdf")
        plt.show()

    def graph_basic_array(self, x_array, y_array, xlabel, ylabel, color_graph):
        plt.plot(x_array, y_array, color=color_graph)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.show()

if __name__ == "__main__":
    # Example usage:
    experiment_plotter = Varian634ExperimentPlotter()
    experiment_plotter.graph(path, sample_reference_file, sample_analyzed_file, sample_analyzed_name, graph_title, peak_search_window)
    experiment_plotter.voltage_curve_display(path, sample_reference_file, sample_analyzed_file, title)
    experiment_plotter.fourier_transformed_display(path, title, FE, sample_reference_file, sample_analyzed_file)
    # Add more function calls as needed
