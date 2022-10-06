# Import statements
import astropy.units as u
import numpy as np
import pandas as pd
import requests
from tletools import TLE

# Get Iridium TLEs
iridium_url = "https://celestrak.com/NORAD/elements/gp.php?GROUP=iridium&FORMAT=tle"
iridium_NEXT_url = "https://celestrak.com/NORAD/elements/gp.php?GROUP=iridium-NEXT&FORMAT=tle"

print("Getting Iridium TLEs...")
iridium_data = requests.get(iridium_url).text
iridium_NEXT_data = requests.get(iridium_NEXT_url).text

# Load TLEs
print("Loading Iridium TLEs...")
iridium_TLEs = TLE.loads(iridium_data)
iridium_NEXT_TLEs = TLE.loads(iridium_NEXT_data)


def get_iridium_state(tle_set):
    r = np.zeros((len(tle_set), 3))
    v = np.zeros((len(tle_set), 3))
    names = []
    epochs = []
    for tle in enumerate(tle_set):
        names.append(tle[1].name)
        epochs.append(tle[1].epoch)
    # epoch_max = max(epochs)
    for tle in enumerate(tle_set):
        # epochs[tle[0]] = epoch_max
        orbit_tmp = tle[1].to_orbit()
        r[tle[0], :] = orbit_tmp.r.to_value(u.m)
        v[tle[0], :] = orbit_tmp.v.to_value(u.m / u.s)
    return names, epochs, r, v


print("Getting Iridium states...")
iridium_names, iridium_epochs, iridium_r, iridium_v = get_iridium_state(iridium_TLEs)
print("Getting Iridium NEXT states...")
iridium_NEXT_names, iridium_NEXT_epochs, iridium_NEXT_r, iridium_NEXT_v = get_iridium_state(iridium_NEXT_TLEs)

iridium_names = [name.replace(" [-]", "") for name in iridium_names]

iridium_dict = {'name': iridium_names, 'epoch': iridium_epochs, 'x': iridium_r[:, 0], 'y': iridium_r[:, 1],
                'z': iridium_r[:, 2], 'vx': iridium_v[:, 0], 'vy': iridium_v[:, 1], 'vz': iridium_v[:, 2]}
iridium_NEXT_dict = {'name': iridium_NEXT_names, 'epoch': iridium_NEXT_epochs, 'x': iridium_NEXT_r[:, 0],
                     'y': iridium_NEXT_r[:, 1], 'z': iridium_NEXT_r[:, 2], 'vx': iridium_NEXT_v[:, 0],
                     'vy': iridium_NEXT_v[:, 1], 'vz': iridium_NEXT_v[:, 2]}

iridium_data = pd.DataFrame(iridium_dict)
iridium_data = iridium_data[~iridium_data.name.str.contains("DUMMY")]  # remove dummy satellites
iridium_NEXT_data = pd.DataFrame(iridium_NEXT_dict)
iridium_all_data = iridium_data.merge(iridium_NEXT_data, how='outer',
                                      on=['name', 'epoch', 'x', 'y', 'z', 'vx', 'vy', 'vz'])

print("Done with Iridium TLEs.")
