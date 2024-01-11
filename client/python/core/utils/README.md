# Test des fonctions de utils

## Test python draw_curve.py

```
    path="C:/Users/admin/Desktop/Projet_GP/Programmation_Spectro/varian-634-app/experiments/Manip_2023/Manip_06_2023/30_06_2023/Fente_2nm/"
    sample_reference_file="Tension_blanc_30_06_2023_Fente_2nm.csv"
    sample_analyzed_file="Tension_echantillon_30_06_2023_Fente_2nm.csv"
    sample_analyzed_name="bleu de bromophénol"
    graph_title="Absorbance du " + sample_analyzed_name
    date="27/11/2023"

    graph(path, sample_reference_file, sample_analyzed_file, sample_analyzed_name, graph_title, peak_search_window=20)
    voltage_curve_display(path, title="voltage and wavelenght", sample_reference_file=sample_reference_file, sample_analyzed_file=sample_analyzed_file)
    fourier_transformed_display(path=path, title="Transformée de Fourier", FE=250000)# fréquence d'échantillonage de la carte NI-PCI 

```


## Test python save_data_csv
```
path = "C:/Users/admin/Desktop/Projet_GP/Programmation_Spectro/varian-634-app/client/python/core/utils"
file_name = "Test_program_save_data.csv"
data_list = [[1, 2, 3, 4, 4, 5], ["gregerge", "rgeg", "grgreg"], [545,55757]]
title_list = ["Liste 1", "Liste 2", "rgrzgzrgz"]
save_data_csv(path, file_name, data_list, title_list)
```

## 

```
experiment_manager = ExperimentManager()
path, date, slot_size = experiment_manager.creation_directory_date_slot()
physical_data_path = experiment_manager.path_creation(path, "physical_data")
experiment_manager.delete_files_in_directory(physical_data_path)
```