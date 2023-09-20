
import time 



# Motors
from core.kinematic_chains.screw_motor import state_screw_motor, grbl_parameter_screw_motor, initialisation_motor_screw, move_screw, return_screw
from core.kinematic_chains.mirror_cuves_motor import move_mirror_cuves_motor , initialisation_mirror_cuves_motor
from core.kinematic_chains.end_stop_sensor import *

# Voltage acquisition
from core.electronics_controler.ni_pci_6621 import voltage_acquisition , get_solution_cuvette

# Data processing
from core.utils.save_data_csv import save_data_csv
from core.utils.draw_curve import graph









"""
ACQUISITION DU SIGNAL
"""
def precision_mode(S, PIN, screw_travel, number_measurements, screw_translation_speed, PULSE_FREQUENCY, DUTY_CYCLE, SAMPLES_PER_CHANNEL, SAMPLE_RATE, CHANNELS):  
    """
    Entrée :
        - S: Méthode pour intéragir avec l'arduino
        - screw_travel: distance parcourue par la vis en mm 
        - number_measurements: nombre de mesure de tension en Volt
        - screw_translation_speed: vitesse de translation de la vis (mm/min)
    
    Sortie : 
    
    """
    
    voltages_photodiode_1= []
    voltages_photodiode_2= []

    wavelength=[]
    no_screw=[] 
    i=0
    step=screw_travel/number_measurements # 0.5mm Pas de la vis (cf Exel)
    time_per_step= (step*60)/screw_translation_speed # Temps pour faire un pas 
    

    """
    Initialisation cuves
    """
    choice = get_solution_cuvette()

    """
    Initialisation moteur    
    """
    initialisation_mirror_cuves_motor(S,PIN)

    initialisation_motor_screw(S,screw_translation_speed)
    

    # Hypothèse : La photodiode 1 est toujours branché sur le port 'ai0' et la photodiode 2 toujours branché sur le port 'ai1'

    """
    Début de l'acquisition
    """
    while i < screw_travel: # Tant que la vis n'a pas parcouru une distance course_vis
        voltage_photodiode_1 = voltage_acquisition(SAMPLES_PER_CHANNEL, SAMPLE_RATE, PULSE_FREQUENCY, DUTY_CYCLE, CHANNELS, channel='ai0')
        voltages_photodiode_1.append(voltage_photodiode_1)

        move_mirror_cuves_motor(S, 0.33334)  # Le moteur doit faire une angle de 60°
        time.sleep(0.5)
        
        voltage_photodiode_2 = voltage_acquisition(SAMPLES_PER_CHANNEL, SAMPLE_RATE, PULSE_FREQUENCY, DUTY_CYCLE, CHANNELS, channel='ai1')
        voltages_photodiode_2.append(voltage_photodiode_2)

        move_mirror_cuves_motor(S, -0.33334)  # Le moteur doit faire une angle de 60°
        time.sleep(0.5)

        no_screw.append(i)
        wavelength.append(-31.10419907 * i + 800)  # cf rapport 2022-2023 dans la partie "Acquisition du signal"

        move_screw(S, i + step)  # Le moteur travail en mode absolu par défaut G90

        print(f"Tension photodiode 1 (Volt) : {voltages_photodiode_1}")
        print(f"Taille de la liste Tension photodiode 1 : {len(voltages_photodiode_1)}")
        print(f"Tension photodiode 2 (Volt) : {voltages_photodiode_2}")
        print(f"Taille de la liste photodiode 2 : {len(voltages_photodiode_2)}")
        print(f"Pas de vis (mm) : {i}")
        print(f"Longueur d'onde (nm) : {wavelength}")
        print(f"Taille de la liste Longueur d'onde (nm) : {len(wavelength)}")

        time.sleep(time_per_step)  # Comme $110 =4mm/min et le pas de vis est de 0.5mm => Le moteur réalise un pas de vis en 7.49s
        i += step

        
        

    """
    Fin de l'acquisition
    """

    """
    Donner le numéro de la cuve qui contient la solution de référence (solvant)
    """
    if choice == 'cuve 1':
        reference_solution=voltages_photodiode_1
        sample_solution=voltages_photodiode_2
    else:
        reference_solution=voltages_photodiode_2
        sample_solution=voltages_photodiode_1



   
    wavelength.reverse()
    reference_solution.reverse()
    sample_solution.reverse()
    no_screw.reverse()

    return  wavelength, reference_solution, sample_solution, no_screw


def acquition(S, screw_travel, number_measurements, screw_translation_speed, file_reference_solution, sample_solution_file, sample_solution_name, title, REPERTORY): # Départ 7.25mm / 21 - 7.25 = 13.75mm où 21 course de la vis total de la vis => screw_travel=13.75mm
    column_name_voltages_reference_solution='Tension blanc (Volt)'

    column_name_voltages_sample_solution='Tension échantillon (Volt)'

   
  


    [wavelength, voltages_reference_solution, voltages_sample_solution, no_screw] = precision_mode(S,screw_travel, number_measurements, screw_translation_speed)
    

   

    

    
    save_data_csv(sample_solution_file, wavelength, voltages_sample_solution, no_screw, 'Longueur d\'onde (nm)', column_name_voltages_sample_solution,'Liste_pas_vis')
    save_data_csv(file_reference_solution, wavelength, voltages_reference_solution, no_screw, 'Longueur d\'onde (nm)', column_name_voltages_reference_solution,'Liste_pas_vis')

    gcode_state_motor=str(state_screw_motor(S))
    while 'Idle' not in gcode_state_motor: # 'Idle': Instruction GRBL pour dire que ce moteur est à l'arrêt / 'Run' le moteur tourne
        gcode_state_motor=str(state_screw_motor(S))

    print(gcode_state_motor)
    
    grbl_parameter_screw_motor(S)
    return_screw(S,screw_travel, screw_translation_speed=10)
    grbl_parameter_screw_motor(S)    

    graph(file_reference_solution, sample_solution_file, sample_solution_name, title, REPERTORY)
