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
            $0=10 (step pulse, usec)
            $1=25 (step idle delay, msec)
            $2=0 (step port invert mask:00000000)
            $3=0 (dir port invert mask:00000000)
            $4=0 (step enable invert, bool)
            $5=0 (limit pins invert, bool)
            $6=0 (probe pin invert, bool)
            $10=3 (status report mask:00000011)
            $11=0.010 (junction deviation, mm)
            $12=0.002 (arc tolerance, mm)
            $13=0 (report inches, bool)
            $20=0 (soft limits, bool)
            $21=1 (hard limits, bool)
            $22=1 (homing cycle, bool)
            $23=1 (homing dir invert mask:00000001)
            $24=6.000 (homing feed, mm/min)
            $25=10.000 (homing seek, mm/min)
            $26=250 (homing debounce, msec)
            $27=1.000 (homing pull-off, mm)
            $100=10295.660 (x, step/mm)
            $101=3200.000 (y, step/mm)
            $102=3200.000 (z, step/mm)
            $110=10.000 (x max rate, mm/min)
            $111=10.000 (y max rate, mm/min)
            $112=20.000 (z max rate, mm/min)
            $120=10.000 (x accel, mm/sec^2)
            $121=10.000 (y accel, mm/sec^2)
            $122=10.000 (z accel, mm/sec^2)
            $130=21.000 (x max travel, mm)
            $131=200.000 (y max travel, mm)
            $132=200.000 (z max travel, mm)
        ```
    6. Modification code grbl : config.h (mettre le code)


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

