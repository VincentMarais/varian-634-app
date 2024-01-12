# Test des fonctions de utils

## Test python draw_curve.py

```
    path="./experiments/experiments_2023/experiments_12_2023/experiments_15_12_2023/Fente_2nm"
    sample_analyzed_name="bleu de bromophénol"
    peak_search_window=2
    file_experiment=15_12_2023_Fente_2nm_Gael.csv
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