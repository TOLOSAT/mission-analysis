import pandas as pd
from os import listdir

files = [file.split(".")[0] for file in listdir("iridium_states")]
results = {}
for file in files:
    results[file] = pd.read_pickle(f"iridium_states/{file}.pkl")
    column_names = ["x", "y", "z", "vx", "vy", "vz"]
    if file != "epochs":
        columns = {}
        for column in enumerate(list(results[file].columns)):
            columns[column[1]] = column_names[column[0]]

        results[file].rename(columns=columns, inplace=True)