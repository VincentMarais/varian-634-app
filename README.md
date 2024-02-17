# Automatisation d'un spectrophotomètre Varian 634 avec Python

Ce programme Python permet d'automatiser un ancien spectrophotomètre Varian 634. Il permet d'acquérir la tension de la photodiode à l'aide d'une carte NI-PCI 6221, de piloter le réseau de diffraction du spectrophotomètre avec un moteur, de contrôler l'alternance du faisceau lumineux afin de faire fonctionner le spectrophotomètre Varian 634 en mode double faisceau, et de traiter le signal d'absorbance de la solution pour éliminer le bruit de mesure.

# Installation des bibliothèques Python avec pip

## Prérequis
. Python 3.x installé sur votre machine - https://www.python.org/downloads/
. Télécharger le code varian-634-app sur GitHub

## Installation
1. Ouvrez une invite de commande ou un terminal sur votre machine.


2. Assurez-vous que `pip` est installé en exécutant la commande suivante :

```bash
pip --version
```

Si `pip` n'est pas installé, suivez les étapes de ce tutoriel : 

https://www.youtube.com/watch?v=PikcUT-ts7E&ab_channel=AhmedHegazy 

3. Dézipper le fichier :  varian-634-app-main.zip

4. Placez-vous dans le répertoire du fichier varian-634-app-main .

``` bash
cd Chemin_acces
```
Exemple si vous avez téléchargé le fichié sur votre bureau: 

``` bash
cd Desktop\varian-634-app-main
```


4. Installez les bibliothèques nécessaires en exécutant la commande suivante :

``` bash
pip install -r requirements.txt
```
Cette commande va installer toutes les bibliothèques listées dans le fichier requirements.txt qui se trouve dans le répertoire du projet. Assurez-vous que ce fichier contient bien toutes les bibliothèques nécessaires au bon fonctionnement du programme.

# Utilisation du programme

1. Brancher les cartes arduino sur l'ordinateur.

2. Allumez le spectrophotomètre Varian 634 et assurez-vous qu'il est correctement connecté à l'ordinateur.

3. Ouvrez un terminal dans le dossier du programme.

4. Lancez le programme avec la commande suivante :

``` bash
python client\app.py
```

5. Suivez les instructions affichées à l'écran pour utiliser l'application.



# Mise à jour des bibliothèques

Pour mettre à jour les bibliothèques Python installées avec pip, vous pouvez utiliser la commande suivante :

``` bash
pip install --upgrade -r requirements.txt
```

Cette commande va mettre à jour toutes les bibliothèques listées dans le fichier requirements.txt vers leur dernière version disponible.

# Auteur

Ce programme a été développé par l'équipe spectrophotomètre en génie physique à Polytech Clermont.

## Suivez-nous sur Instagram

Suivez-nous sur [Instagram](https://www.instagram.com/varian_634_renovation/) pour découvrir les dernières nouvelles et les coulisses de notre projet.  

<a href="https://instagram.com/varian_634_renovation" target="blank"><img align="center" src="https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/instagram.svg" alt="varian_634_renovation" height="30" width="40" /></a>
</p> 

