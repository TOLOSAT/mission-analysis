import pandas as pd
from os import listdir


def get_list_of_contents(path):
    return [file.split(".")[0] for file in listdir(path)]


def get_results_dict(path):
    files = get_list_of_contents(path)
    results_dict = {}
    for file in files:
        results_dict[file] = pd.read_pickle(f"{path}/{file}.pkl")
        column_names = ["x", "y", "z", "vx", "vy", "vz"]
        if file != "epochs":
            columns = {}
            for column in enumerate(list(results_dict[file].columns)):
                columns[column[1]] = column_names[column[0]]

            results_dict[file].rename(columns=columns, inplace=True)
    return results_dict
