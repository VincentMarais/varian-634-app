"""
This program will create the baseline for the absorbance analysis of the sample.

"""

# Supprimmer le bruit de noir
def correction_bruit_de_noir(noise_absorption, absorbance_solution):
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



# End-of-file (EOF)