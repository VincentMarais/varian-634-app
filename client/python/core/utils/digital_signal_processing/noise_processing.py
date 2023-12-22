"""
This program will reduce the noise from the photodiode"""
import numpy as np


def negative_absorbance_correction(voltage_sample_reference, voltage_sample_analyzed):
    """
    Entrée : 
        - voltage_sample_reference (liste) : Liste des tensions mesurer aux bornes de la photodiode où il y a la cuve de la solution de blanc.

        - voltage_sample_analyzed (liste) : Liste des tensions mesurer aux bornes de la photodiode où il y a la cuve de l'échantillon.

    Sortie :
        - voltage_sample_reference (liste) : Liste des tensions mesurer aux bornes de la photodiode où il y a la cuve de la solution de blanc.

        - voltage_sample_analyzed (liste) : Liste des tensions mesurer aux bornes de la photodiode où il y a la cuve de l'échantillon corrigé, 
        c'est à dire que pour toute voltage_sample_analyzed[i] et voltage_sample_reference[i] on a :
                                voltage_sample_analyzed[i] =< voltage_sample_reference[i]
        
    BUT : Supprimer les absorbance négative pour être en accord avec la réalité physique de notre solution 
    (cf Rapport 2022-2023 pour plus de détaille sur la physique du problème)
-
    """
    for i in range (len(voltage_sample_reference)):

        if np.abs(voltage_sample_reference[i]) < np.abs(voltage_sample_analyzed[i]): # Ce qui est possible s'il y a du bruit de mesure 
            voltage_sample_analyzed[i]=voltage_sample_reference[i]

    return voltage_sample_reference, voltage_sample_analyzed




def voltage_possessing(door_function_width, voltage):
    """
    This program will perform voltage denoising (cf Report 2022-2023 for the professor).

    Entry: door_function_width 35 # optimal settings (Slit 0.2mm): 23 /
            (Slit 0.5mm): 30 / (Slit 1mm): 15 / (Slit 2mm): 30 (# Define the smoothing window size)
    voltage (list)  """

    voltage=np.convolve(voltage, np.ones(door_function_width)/door_function_width, mode='same') 
    return voltage


def correction_bruit_de_noir(baseline_absorbance, absorbance_solution):
    """
    Entrée : 
        - noise_absorption (liste) : L'absorbance de noir est l'absorbance mesurée pour chaque longueur d'onde avec 
        une largeur de fente donnée. Lorsqu'il n'y a pas de cuve, l'absorbance mesurée doit être nulle si :

            L'intensité lumineuse mesurée sur la photodiode 1 = l'intensité lumineuse mesurée sur la photodiode 2. 
         
        Cependant, étant donné que les capteurs sont différents, L'absorbance de noir n'est pas nulle pour toute les longueur d'onde.


        - absorbance_solution (liste) : absorbance_solution est l'absorbance mesurée pour chaque longueur d'onde avec 
        une largeur de fente donnée. Lorqu'il y a les deux cuves avec des solutions à l'intérieurs.

    Sortie :

        - Absorbance_corrige (liste) : Absorbance où l'on a supprimer l'absorbance de noir pour chaque longueur d'onde.

    BUT : Avoir des valeurs cohérente d'absorbances de notre solution pour chaque longueur d'onde.
    """
    pass