# Import statements
from datetime import datetime

import numpy as np
import pandas as pd
import requests
from tqdm import tqdm
from tudatpy.kernel.astro.element_conversion import mean_motion_to_semi_major_axis, \
    mean_to_true_anomaly
from tudatpy.kernel.interface import spice
from tudatpy.kernel.numerical_simulation import environment_setup

from useful_functions.date_transformations import datetime_to_epoch

# Load spice kernels
spice.load_standard_kernels([])

# Create default body settings and bodies system
bodies_to_create = ["Earth"]
global_frame_origin = "Earth"
global_frame_orientation = "J2000"
body_settings = environment_setup.get_default_body_settings(
    bodies_to_create, global_frame_origin, global_frame_orientation)
bodies = environment_setup.create_system_of_bodies(body_settings)

earth_mu = bodies.get_body("Earth").gravitational_parameter

# Get Iridium TLEs
iridium_url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=iridium-NEXT&FORMAT=json"

iridium_data = pd.read_json(requests.get(iridium_url).text)

iridium_data["MEAN_MOTION"] = iridium_data["MEAN_MOTION"] * 2 * np.pi / 86400
iridium_data["MEAN_ANOMALY"] = np.deg2rad(iridium_data["MEAN_ANOMALY"])
iridium_data['sma'] = pd.Series(dtype='float64')
iridium_data['tan'] = pd.Series(dtype='float64')
for i in tqdm(range(len(iridium_data)), desc='TLEs', ncols=80):
    iridium_data.iloc[i, iridium_data.columns.get_indexer(["sma"])] = mean_motion_to_semi_major_axis(
        iridium_data.iloc[i].loc["MEAN_MOTION"], earth_mu)
    iridium_data.iloc[i, iridium_data.columns.get_indexer(["tan"])] = mean_to_true_anomaly(
        iridium_data.iloc[i].loc["ECCENTRICITY"],
        iridium_data.iloc[i].loc["MEAN_ANOMALY"])
    iridium_data.iloc[i, iridium_data.columns.get_indexer(["EPOCH"])] = datetime_to_epoch(
        datetime.strptime(iridium_data.iloc[i]["EPOCH"], "%Y-%m-%dT%H:%M:%S.%f"))

iridium_data.rename(columns={"OBJECT_NAME": "name", "EPOCH": "epoch", "ECCENTRICITY": "ecc", "INCLINATION": "inc",
                             "ARG_OF_PERICENTER": "aop", "RA_OF_ASC_NODE": "raan"}, inplace=True)
