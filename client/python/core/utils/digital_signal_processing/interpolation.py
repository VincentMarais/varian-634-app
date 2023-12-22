from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt
import pandas as pd

def spline_interpolation(data_x, data_y, tilte_data_x, title_data_y):
    """
    Entrée : 
        - data_y_spline (liste) : data_y calculer après lui avoir appliqué un spline cubique

    Sortie: data_y_spline (liste) : data_y calculer après lui avoir appliqué un spline cubique corrigé, c'est à dire :

                                            Pour tout i, data_y_spline[i] >= 0
    
    

    BUT : Supprimer les data_y négative pour être en accord avec la réalité physique de notre solution 
    (cf Rapport 2022-2023 pour plus de détaille sur la physique du problème)

    
    """
    spline = UnivariateSpline(data_x, data_y, s=20)
    data_y_spline = spline(data_x)
    for i in range(len(data_y_spline)):
        if data_y_spline[i] < 0:
            data_y_spline[i]=0
    plt.figure()
    plt.plot(data_x, data_y, '-', label='Données bruitées')
    plt.plot(data_x, data_y_spline, '--', label='data interpolate cubic spline')
    plt.legend()
    plt.xlabel(tilte_data_x)
    plt.ylabel(title_data_y)
    plt.show()
    return data_y_spline



def sample_absorbance(absorbance_baseline, absorbance_scanning, pas_scanning, nom_fichier_baseline):
    data_baseline = pd.read_csv(nom_fichier_baseline, encoding='ISO-8859-1')
    absorbance_baseline = data_baseline['Absorbance']
    absorbance_baseline_acquisition=[]
    sample_absorbance=[]
    for i in range (0,len(absorbance_baseline),pas_scanning):
        absorbance_baseline_acquisition.append(absorbance_baseline[i])
    for i in range(absorbance_scanning):
        diff=absorbance_scanning[i] - absorbance_baseline_acquisition[i]
        sample_absorbance.append(diff)
    return sample_absorbance



