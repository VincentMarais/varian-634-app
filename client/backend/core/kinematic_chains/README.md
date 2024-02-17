# Guide d'utilisation de CNC Shield avec GRBL et Python

Ce guide fournit des instructions pour configurer et utiliser une CNC Shield avec GRBL via une interface Python. Assurez-vous de suivre chaque étape attentivement pour une configuration réussie.

## Prérequis

- CNC Shield équipée de GRBL
- Arduino Uno (ou compatible)
- Python 3.x installé sur votre ordinateur
- Accès terminal ou ligne de commande
- Bibliothèque Python `pyserial` pour la communication série

## Installation

1. **Configuration de l'environnement Arduino:**
   1. Assurez-vous que GRBL est téléchargé et installé sur votre Arduino. Consultez [la page GitHub de GRBL](https://github.com/gnea/grbl) pour les instructions détaillées.
    2. Connectez votre Arduino à votre ordinateur via USB.

    3. Assurez-vous que le code "grbl.ino" a été téléversé sur la carte Arduino avec la CNC shield.

    4. Ouvrez le terminal série de l'Arduino en tapant la commande suivante : "$$"

    5. Assurez-vous que les paramètres si-dessous sont correctement configurés avant de tester les moteurs
        ```
            $0=10
            $1=25
            $2=0
            $3=0
            $4=0
            $5=0
            $6=0
            $10=1
            $11=0.010
            $12=0.002
            $13=0
            $20=0
            $21=1
            $22=1
            $23=0
            $24=10.000
            $25=12.000
            $26=250
            $27=1.000
            $30=1000
            $31=0
            $32=0
            $100=10295.660
            $101=3200.000
            $102=3200.000
            $110=10.000
            $111=10.000
            $112=10.000
            $120=200.000
            $121=10.000
            $122=10.000
            $130=21.000
            $131=800.000
            $132=800.000
        ```

2. **Installation Python et pyserial:**
   - Si Python n'est pas installé, téléchargez-le depuis [le site officiel de Python](https://www.python.org/downloads/) et suivez les instructions d'installation.
   - Installez `pyserial` en utilisant pip, le gestionnaire de paquets Python :
     ```
     pip install pyserial
     ```

## Configuration

- Assurez-vous que le port série de votre Arduino est correctement sélectionné et que la vitesse de baud correspond à celle configurée dans GRBL (115200 par défaut).
- Pour vérifier les ports disponibles, vous pouvez utiliser le moniteur série de l'IDE Arduino ou exécuter le script Python suivant :

  ```python
  import serial.tools.list_ports
  ports = serial.tools.list_ports.comports()
  for port in ports:
      print(port)
    ```

## GRBL

Modification du code source : config.h et limit.c

