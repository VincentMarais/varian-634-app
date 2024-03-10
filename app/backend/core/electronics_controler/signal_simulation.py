"""
Programme de simulation signal des photodiode
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Paramètres
longueur = 100000  # Longueur de la série de données
periode = 2500  # Période à laquelle la fonction prend une valeur non nulle
peak_search_window = periode
def photodiode_voltages_simu():
    """
    Simulation de la tension des photodiode
    """
    # Génération des données
    x = np.arange(0,1,1/longueur)
    y = np.zeros(longueur)
    a = np.random.uniform(0.3, 1.1, longueur // periode)

    for i in range(len(a)):
        y[i * periode] = a[i] * -1

    # Nota : écart type mini bien avec log opti pour des valeurs < -1 
    # Sinon pour des valeurs au-dessus de > -1 la moyennes c'est mieux

    # Ajout de bruit
    bruit = np.random.normal(0, 0.0058, longueur)  # Moyenne 0, écart-type 0.5
    y += bruit
    y_dect= -y
    peaks, _ = find_peaks(y_dect, distance=peak_search_window)
    # Conversion des données en un tableau numpy pour faciliter les calculs
    # Convertir les indices des pics en un array python
    peak_voltages = -np.array([y_dect[i] for i in peaks])
    return x, y, peaks, peak_voltages

[x, y, peaks, peaks_voltages] = photodiode_voltages_simu()

# Affichage des données
plt.figure(figsize=(10, 6))
plt.plot(x, y, label="Tension photodiode simulé")
plt.xlabel("Temps (s)", fontsize=14)
plt.ylabel("Tension (Volt)", fontsize=14)
plt.title("Tension photodiode simulé")
plt.legend()
plt.grid(True)
plt.show()

# Affichage des pics
plt.figure(figsize=(10, 6))
plt.plot(x, y, label="Tension photodiode simulé")
plt.plot(x[peaks], peaks_voltages, "x", color='red', label="Pics")
plt.xlabel("Temps (s)", fontsize=14)
plt.ylabel("Tension (Volt)", fontsize=14)
plt.title("Pics du signal simulé")
plt.legend()
plt.grid(True)  
plt.show()

mediane_par_instant = np.median(peaks_voltages)
moyenne_pic=np.mean(peaks_voltages)
print("mediane_par_instant", mediane_par_instant)
print("moyenne_pic", moyenne_pic )

N = 3  # Nombre de signaux

moyennes= []
medianes = []
mini=[]
# Génération des N signaux
signaux = np.zeros((N, longueur))
for i in range(N):
    [x, y, peaks, peaks_voltages] = photodiode_voltages_simu()
    mini.append(np.min(y))
    mediane_par_instant = np.median(peaks_voltages)
    moyenne_par_instant= np.mean(peaks_voltages)
    moyennes.append(moyenne_par_instant)
    medianes.append(mediane_par_instant)

x_2 = np.arange(N)
    

# Calcul de la médiane à chaque instant

# Affichage de la médiane des signaux
plt.figure(figsize=(10, 6))
plt.plot(x_2, medianes, label="Médiane à chaque instant", color="red")
plt.plot(x_2, moyennes, label="moyenne à chaque instant", color="blue")
plt.plot(x_2, mini ,label="mini à chaque instant")
plt.axhline(y=np.median(np.array(moyennes)), color='r', linestyle='-', label="mediane moyennes pics")
plt.axhline(y=np.mean(np.array(moyennes)), color='g', linestyle='-', label="moyenne de la moyennes pics")
plt.axhline(y=np.median(np.array(medianes)), color='b', linestyle='-', label="mediane de la medianes pics")
plt.axhline(y=np.mean(np.array(medianes)), color='y', linestyle='-', label="moyenne de la medianes pics")
plt.axhline(y=np.mean(np.array(mini)), color='y', linestyle='-', label="moyenne des mini pics")




plt.xlabel("Temps")
plt.ylabel("Valeur")
plt.title("Médiane des valeurs à chaque instant pour N signaux")
plt.legend()
plt.grid(True)
plt.show()

# Calcul de l'écart-type
ecart_type_medianes = np.std(medianes)
ecart_type_moyennes = np.std(moyennes)
ecart_type_mini = np.std(mini)
ecart_type_peak=np.std(-peaks_voltages)


print(f"L'écart-type de medianes est: {ecart_type_medianes}")
print(f"L'écart-type de moyennes est: {ecart_type_moyennes}")
print(f"L'écart-type de mini est: {ecart_type_mini}")
print(f"L'écart-type des peak est: {ecart_type_peak}")

import scipy.signal as signal



# Signal d'exemple
x = np.random.randn(100)  # Un signal aléatoire

# Filtrage passe-bas
b, a = signal.butter(4, 0.05)
y_filtre = signal.filtfilt(b, a, x)

# Affichage
plt.figure(figsize=(10, 6))
plt.plot(x, label='Signal original')
plt.plot(y_filtre, label='Signal filtré')
plt.xlabel('Temps')
plt.ylabel('Amplitude')
plt.title('Filtrage passe-bas avec Butterworth')
plt.legend()
plt.grid(True)
plt.show()

def moyenne_mobile(x, N=5):
    return np.convolve(x, np.ones(N)/N, mode='valid')

# Signal d'exemple
x = np.random.randn(100)

# Application de la moyenne mobile
y_moyenne_mobile = moyenne_mobile(x)

# Affichage
plt.figure(figsize=(10, 6))
plt.plot(x, label='Signal original')
plt.plot(y_moyenne_mobile, label='Moyenne mobile (N=5)')
plt.xlabel('Temps')
plt.ylabel('Amplitude')
plt.title('Application de la moyenne mobile')
plt.legend()
plt.grid(True)
plt.show()


medianes=-np.array(medianes)
moyennes=-np.array(moyennes)
mini=-np.array(mini)

plt.figure(figsize=(10, 6))
plt.plot(x_2, np.log(medianes), label="Médiane à chaque instant", color="red")
plt.plot(x_2, np.log(moyennes), label="moyenne à chaque instant", color="blue")
plt.plot(x_2, np.log(mini) ,label="mini à chaque instant")


# Calcul de l'écart-type
ecart_type_medianes = np.std(np.log(medianes))
ecart_type_moyennes = np.std(np.log(moyennes))
ecart_type_mini = np.std(np.log(mini))
ecart_type_peak=np.std(np.log(-peaks_voltages))

print(f"L'écart-type de medianes log est: {ecart_type_medianes}")
print(f"L'écart-type de moyennes log est: {ecart_type_moyennes}")
print(f"L'écart-type de mini log est: {ecart_type_mini}")
print(f"L'écart-type de peak log est: {ecart_type_peak}")


plt.xlabel("Temps")
plt.ylabel("Valeur")
plt.title("Médiane des valeurs à chaque instant pour N signaux")
plt.legend()
plt.grid(True)
plt.show()