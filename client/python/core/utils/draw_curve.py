"""
Program pour les graphiques
"""

import matplotlib.pyplot as plt
import numpy as np
from data_csv import CSVTransformer
from scipy.signal import find_peaks
import pandas as pd

class Varian634ExperimentPlotter:
    """
    class pour afficher les graphes après acquisition
    """
    def __init__(self, path, sample_analyzed_name, peak_search_window):
        self.path = path
        self.sample_analyzed_name = sample_analyzed_name
        self.csv_file = CSVTransformer(self.path)
        self.peak_search_window = peak_search_window


    def max_absorbance_display(self, wavelength_peak, absorbance_peak, wavelength, absorbance):
        """
        Fonction pour afficher les pics d'absorbance et 
        le max d'absorbance 
        """
        plt.scatter(wavelength_peak, absorbance_peak, color='red')

        plt.annotate(f'({wavelength_peak:.2f} nm, {absorbance_peak:.2f})',
                     xy=(wavelength_peak, absorbance_peak),
                     xytext=(wavelength_peak + 10, absorbance_peak),
                     fontsize=10,
                     color='red',
                     arrowprops=dict(facecolor='red', arrowstyle='->'))

        plt.hlines(y=absorbance_peak, xmin=wavelength[0], xmax=wavelength_peak, linestyle='dashed', color='red')
        plt.vlines(x=wavelength_peak, ymin=min(absorbance), ymax=absorbance_peak, linestyle='dashed', color='red')

    def graph_absorbance(self, file_experiment):
        """
        Affichage du graph de l'absorbance en fonction 
        de la longueur d'onde

        """
        path_file=f"{self.path}/{file_experiment}.csv"
        data_file_experiment = pd.read_csv(path_file, encoding='ISO-8859-1')

        wavelength= data_file_experiment['Longueur d\'onde (nm)']

        absorbance = data_file_experiment['Absorbance']
        absorbance_peak = max(absorbance)

        wavelength_peak = wavelength[np.argmax((absorbance))]        
        peaks, _ = find_peaks(absorbance, distance=self.peak_search_window)
        titles_list_peak=["absorbance pics", "longueur d'onde pics"]
        self.csv_file.add_column_to_csv(file_experiment, titles_list_peak, [peaks, wavelength[peaks]])        
        graph_title='Absorbance du ' + self.sample_analyzed_name
        plt.plot(wavelength, absorbance)
        plt.plot(wavelength[peaks], absorbance[peaks], 'ro')

        plt.xlabel('Longueur d\'onde (nm)')
        plt.ylabel('Absorbance')
        plt.title(graph_title)
        self.max_absorbance_display(wavelength_peak, absorbance_peak, wavelength, absorbance)
        plt.savefig(self.path + '\\' + graph_title + ".pdf")
        plt.show()

    def classic_graph(self, datas_x , datas_y, title_graph, titles_data_y, y_name):
        """
        Plot classique graph 
        - Entry:
            - datas_x = [data_x, name_data_x]

        """
        plt.figure()
        for data_y, title_data_y in zip(datas_y, titles_data_y):
            plt.plot(datas_x[0], data_y, '-', label=title_data_y)
        plt.legend()
        plt.xlabel(datas_x[1])
        plt.ylabel(y_name)
        plt.title(title_graph)
        plt.show()

if __name__ == "__main__":
    # Example usage:
    PATH="./experiments/experiments_2023/experiments_12_2023/experiments_15_12_2023/Fente_2nm"
    sample_name= input("Nom de l'espèce chimique :")
    WINDOW = 2
    FILE='nom_fichier'
    experiment_plotter = Varian634ExperimentPlotter(PATH, sample_name, WINDOW)
    experiment_plotter.graph_absorbance(FILE)
    # Add more function calls as needed
