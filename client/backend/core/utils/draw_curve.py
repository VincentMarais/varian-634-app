"""
Program for graphics.

"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
import pandas as pd
from utils.experiment_manager import ExperimentManager

class Varian634ExperimentPlotter:
    """
    Classe pour afficher les graphes après acquisition.
    """

    def __init__(self, path, sample_analyzed_name, peak_search_window):
        """
        Constructeur de la classe Varian634ExperimentPlotter.

        Parameters:
            path (str): Le chemin du dossier contenant les fichiers CSV.
            sample_analyzed_name (str): Le nom de l'espèce chimique analysée.
            peak_search_window (int): La fenêtre de recherche des pics.

        Returns:
            None
        """
        self.path = path
        self.sample_analyzed_name = sample_analyzed_name
        self.peak_search_window = peak_search_window


    def max_absorbance_display(self, wavelength_peak, absorbance_peak, wavelength, absorbance):
        """
        Fonction pour afficher les pics d'absorbance et le maximum d'absorbance.

        Parameters:
            wavelength_peak (float): La longueur d'onde du pic d'absorbance maximal.
            absorbance_peak (float): La valeur d'absorbance maximale.
            wavelength (numpy.ndarray): Les longueurs d'onde.
            absorbance (numpy.ndarray): Les valeurs d'absorbance.

        Returns:
            None
        """
        plt.scatter(wavelength_peak, absorbance_peak, color='red')

        plt.annotate(f'({wavelength_peak:.2f} nm, {absorbance_peak:.2f})',
                     xy=(wavelength_peak, absorbance_peak),
                     xytext=(wavelength_peak + 10, absorbance_peak),
                     fontsize=10,
                     color='red',
                     arrowprops=dict(facecolor='red', arrowstyle='->'))

        plt.hlines(y=absorbance_peak,
                   xmin=wavelength[0],
                   xmax=wavelength_peak,
                   linestyle='dashed',
                   color='red')

        plt.vlines(x=wavelength_peak, ymin=min(absorbance),
                   ymax=absorbance_peak,
                   linestyle='dashed',
                   color='red')

    def graph_absorbance(self, file_experiment):
        """
        Affichage du graphique de l'absorbance en fonction de la longueur d'onde.

        Parameters:
            file_experiment (str): Le nom du fichier CSV de l'expérience.

        Returns:
            None
        """
        path_file = f"{self.path}/{file_experiment}.csv"
        data_file_experiment = pd.read_csv(path_file, encoding='ISO-8859-1')

        wavelength = data_file_experiment['Longueur d\'onde (nm)']
        absorbance = data_file_experiment['Absorbance']
        absorbance_peak = max(absorbance)

        wavelength_peak = wavelength[np.argmax((absorbance))]
        peaks, _ = find_peaks(absorbance, distance=self.peak_search_window)
        titles_data = ['Longueur d\'onde (nm)','Absorbance', "Absorbance pics", "Longueur d'onde pics (nm)"]
        data = [wavelength, absorbance, peaks, wavelength[peaks]]
        ExperimentManager().save_data_csv(self.path, data, titles_data, file_experiment)
        graph_title = 'Absorbance du ' + self.sample_analyzed_name
        plt.plot(wavelength, absorbance)
        plt.plot(wavelength[peaks], absorbance[peaks], 'ro')

        plt.xlabel('Longueur d\'onde (nm)')
        plt.ylabel('Absorbance')
        plt.title(graph_title)
        self.max_absorbance_display(wavelength_peak, absorbance_peak, wavelength, absorbance)
        plt.savefig(self.path + '\\' + graph_title + ".pdf")
        plt.show()

    def classic_graph(self, datas_x, datas_y, title_graph, titles_data_y, y_name):
        """
        Plot classique du graphique.

        Parameters:
            datas_x (list): Liste contenant les données x [data_x, name_data_x].
            datas_y (list): Liste des données y à tracer.
            title_graph (str): Titre du graphique.
            titles_data_y (list): Liste des titres des données y.
            y_name (str): Nom de l'axe y.

        Returns:
            None
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
    # Exemple d'utilisation:
    PATH = ExperimentManager().choose_folder()
    SAMPLE_NAME = "BROMO"
    WINDOW = 2
    FILE = '06_02_2024_Fente_0_2nm_final'
    experiment_plotter = Varian634ExperimentPlotter(PATH, SAMPLE_NAME, WINDOW)
    experiment_plotter.graph_absorbance(FILE)
    
    





