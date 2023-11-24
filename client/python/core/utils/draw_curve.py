"""
This program will plot the results of the experiment on the VARIAN 634
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def graph(path, sample_reference_file, sample_analyzed_file, sample_analyzed_name, graph_title):
    """
    # sample_reference_file, sample_analyzed_file: (str) 
    path d'accès des fichiers créés pour l'expérience 

    """
    path_sample_reference=path+ '/'+ sample_reference_file
    path_sample_analyzed=path+ '/'+ sample_analyzed_file
    data_sample_reference = pd.read_csv(path_sample_reference,  encoding='ISO-8859-1')
    data_2= pd.read_csv(path_sample_analyzed,  encoding='ISO-8859-1')
# Obtenir les colonnes 'Longueur d\'onde' et Tension Blanc et Tension échantillon
    wavelength = data_sample_reference['Longueur d\'onde (nm)']
    voltage_sample_reference = data_sample_reference['Tension blanc (Volt)']
    voltage_sample_analyzed= data_2['Tension échantillon (Volt)']
    absorbance=np.log10(np.abs(voltage_sample_reference)/np.abs(voltage_sample_analyzed))
    peak_absorbance=max(absorbance)
    peak_wavelength=wavelength[np.argmax((absorbance))]

# Création du graphique
    plt.plot(wavelength, absorbance)
    plt.xlabel('Longueur d\'onde (nm)')
    plt.ylabel('Absorbance')
    plt.title('Absorbance du '+ sample_analyzed_name)

# Mise en évidence du point de pic en rouge
    plt.scatter(peak_wavelength, peak_absorbance, color='red')


# Annotation des coordonnées du point
    plt.annotate(f'({peak_wavelength:.2f} nm, {peak_absorbance:.2f})',
             xy=(peak_wavelength, peak_absorbance),
             xytext=(peak_wavelength + 10, peak_absorbance),
             fontsize=10,
             color='red',
             arrowprops=dict(facecolor='red', arrowstyle='->'))

# Ligne pointillée reliant le point de pic à l'axe des x
    plt.hlines(y=peak_absorbance, xmin=wavelength[0] , xmax=peak_wavelength, linestyle='dashed', color='red')

# Ligne pointillée reliant le point de pic à l'axe des y
    plt.vlines(x=peak_wavelength, ymin=min(absorbance), ymax=peak_absorbance, linestyle='dashed', color='red')
# Affichage du graphique
    plt.savefig(path +'\\'+ graph_title +".pdf")

    plt.show()  

