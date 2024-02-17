# README pour l'utilisation de la carte NI-PCI 6221

## Introduction

La carte NI-PCI 6221 est une carte d'acquisition de données multifonctions conçue par National Instruments. Elle offre une combinaison de fonctionnalités d'entrée et de sortie analogiques et numériques, rendant ce matériel adapté à une grande variété d'applications industrielles, scientifiques, et de recherche.

<div style="text-align: center;">
    <img src="image/National_Instruments_PCI_6221.jpg" width="400"/>
</div>

## Prérequis

- Un PC avec un slot PCI disponible
- Système d'exploitation supporté (Windows, Linux)
- Logiciel NI-DAQmx pour le contrôle des pilotes et l'interface de programmation

## Installation Matérielle

1. **Éteignez** votre ordinateur et débranchez-le de la source d'alimentation.
2. Retirez le couvercle du PC pour accéder aux slots PCI.
3. Insérez la carte NI-PCI 6221 dans un slot PCI libre, en appliquant une pression uniforme pour s'assurer qu'elle est bien connectée.
4. Replacez le couvercle du PC et reconnectez l'alimentation.

## Configuration Logicielle

### Installation de NI-DAQmx

1. Téléchargez le dernier pilote NI-DAQmx depuis le site de National Instruments.
2. Exécutez le programme d'installation et suivez les instructions à l'écran.
3. Redémarrez votre ordinateur après l'installation pour que les changements prennent effet.

### Configuration de votre matériel

1. Ouvrez NI Measurement & Automation Explorer (NI MAX).
2. Sous l'arborescence "Devices and Interfaces", vous devriez voir la carte NI-PCI 6221 listée.
3. Cliquez droit sur le périphérique et sélectionnez "Test Panel" pour vérifier le fonctionnement de la carte.

## Exemples d'Utilisation

### Exemple de Code d'Entrée Analogique

Voici un exemple simple de code pour lire une tension à partir d'une entrée analogique (ici ai0) avec Python.

```python
import nidaqmx
from nidaqmx.constants import TerminalConfiguration

# Utilisation d'un bloc with pour s'assurer que la tâche est bien fermée après son exécution
with nidaqmx.Task() as task:
    # Ajout d'une voie d'entrée analogique à la tâche
    task.ai_channels.add_ai_voltage_chan("Dev1/ai0",
                                         terminal_config=TerminalConfiguration.RSE,
                                         min_val=-10.0, max_val=10.0)
    
    # Lecture d'une valeur unique à partir de la voie configurée
    data = task.read()

    # Affichage de la valeur lue
    print(f"Data Read: {data:.2f}")
```

# Support et Ressources Additionnelles

Pour plus d'informations, référez-vous à la documentation officielle : <a href="https://www.ni.com/docs/fr-FR/bundle/pci-pxi-usb-6221-specs/page/specs.html">https://www.ni.com/docs/fr-FR/bundle/pci-pxi-usb-6221-specs/page/specs.html</a>
