# Import statements
import astropy.units as u
import numpy as np
import requests
from tletools import TLE

# Get Iridium TLEs
iridium_url = "https://celestrak.com/NORAD/elements/gp.php?GROUP=iridium&FORMAT=tle"
iridium_NEXT_url = "https://celestrak.com/NORAD/elements/gp.php?GROUP=iridium-NEXT&FORMAT=tle"

iridium_data = requests.get(iridium_url).text
iridium_NEXT_data = requests.get(iridium_NEXT_url).text

# Load TLEs
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
        orbit_tmp = tle[1].to_orbit()
        r[tle[0], :] = orbit_tmp.r.to_value(u.m)
        v[tle[0], :] = orbit_tmp.v.to_value(u.m / u.s)
    return names, epochs, r, v


iridium_names, iridium_epochs, iridium_r, iridium_v = get_iridium_state(iridium_TLEs)
iridium_NEXT_names, iridium_NEXT_epochs, iridium_NEXT_r, iridium_NEXT_v = get_iridium_state(iridium_NEXT_TLEs)
