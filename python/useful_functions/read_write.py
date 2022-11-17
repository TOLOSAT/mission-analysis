import csv
from os import makedirs

import numpy as np

output_columns = ["time", "eci_x", "eci_y", "eci_z", "eci_vx", "eci_vy", "eci_vz", "kep_sma", "kep_ecc", "kep_inc",
                  "kep_aop", "kep_raan", "kep_ta", "ecef_x", "ecef_y", "ecef_z", "ecef_vx", "ecef_vy", "ecef_vz"]


def write_results(spacecraft_name, orbit_name, dates_name, array):
    """
    Export propagation results to a CSV file.
    """
    makedirs('results/', exist_ok=True)
    for ii in enumerate(output_columns):
        np.savetxt(f'results/{spacecraft_name}_{orbit_name}_{dates_name}_{ii[1]}.csv', array, delimiter=",")


# Function to open csv file and convert data to float array
def open_csv(path, target_file, is_string=False):
    tmp = []
    with open(path + "\\" + target_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if is_string:
                tmp.append(','.join(row))
            else:
                if len(row) == 1:
                    tmp.append(float(row[0]))
                else:
                    tmp.append([float(ii) for ii in row])
    if is_string:
        return tmp
    else:
        return np.array(tmp)
