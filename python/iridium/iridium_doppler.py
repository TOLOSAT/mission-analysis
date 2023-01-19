import numpy as np
import pandas as pd

from results_processing import results
from useful_functions import date_transformations as dt

c = 299792458  # m/s
f0 = 1621.25e6  # H
delta_f_limit = 37500  # Hz doppler shift max +/-
delta_f_dot_limit = 350  # 375  # Hz/s doppler rate max +/-
semi_angle_limit_tolosat = 30  # deg semi-angle visibility
semi_angle_limit_iridium = 30  # deg semi-angle visibility
# pointage zenith // pointage soleil ??

zenith = results["Tolosat"][["x", "y", "z"]]
zenith = zenith / np.linalg.norm(zenith, axis=1)[:, None]
sat_sun = results["sun_position"] - zenith
sat_sun = sat_sun / np.linalg.norm(sat_sun, axis=1)[:, None]
tmp_vector = np.cross(sat_sun, zenith)
top_pointing = np.cross(tmp_vector, sat_sun)

print("Starting Iridium Doppler analysis...")
IRIDIUM_visibility = [results["epochs"].copy().rename("epochs")]
for sat in results:
    if "IRIDIUM" not in sat:
        continue
    else:
        iridium_position = results[sat][["x", "y", "z"]].to_numpy()
        dx = (results[sat]["x"] - results["Tolosat"]["x"]).to_numpy()
        dy = (results[sat]["y"] - results["Tolosat"]["y"]).to_numpy()
        dz = (results[sat]["z"] - results["Tolosat"]["z"]).to_numpy()
        results[sat]["dx"] = dx
        results[sat]["dy"] = dy
        results[sat]["dz"] = dz
        relative_position = np.array([dx, dy, dz]).T

        dv_x = (results[sat]["vx"] - results["Tolosat"]["vx"]).to_numpy()
        dv_y = (results[sat]["vy"] - results["Tolosat"]["vy"]).to_numpy()
        dv_z = (results[sat]["vz"] - results["Tolosat"]["vz"]).to_numpy()
        results[sat]["dv_x"] = dv_x
        results[sat]["dv_y"] = dv_y
        results[sat]["dv_z"] = dv_z
        relative_velocity = np.array([dv_x, dv_y, dv_z]).T
        dv = np.sqrt(dv_x ** 2 + dv_y ** 2 + dv_z ** 2)
        results[sat]["dv"] = dv

        theta_r = np.arccos(np.sum(relative_position * relative_velocity, axis=1) / (
                np.linalg.norm(relative_position, axis=1) * np.linalg.norm(relative_velocity, axis=1)))
        results[sat]["theta_r_deg"] = np.deg2rad(theta_r)
        beta = dv / c
        gamma = 1 / np.sqrt(1 - beta ** 2)

        results[sat]["doppler_shift"] = f0 * (1 / (gamma * (1 + beta * np.cos(theta_r))) - 1)
        results[sat]["doppler_rate"] = np.gradient(results[sat]["doppler_shift"], results["epochs"])

        tolosat_angle = np.arccos(np.sum(relative_position * top_pointing, axis=1) / (
                np.linalg.norm(relative_position, axis=1) * np.linalg.norm(top_pointing, axis=1)))
        results[sat]["tolosat_angle"] = np.rad2deg(tolosat_angle)

        iridium_angle = np.arccos(np.sum(relative_position * iridium_position, axis=1) / (
                np.linalg.norm(relative_position, axis=1) * np.linalg.norm(iridium_position, axis=1)))
        results[sat]["iridium_angle"] = np.rad2deg(iridium_angle)

        results[sat]["doppler_shift_OK"] = np.abs(results[sat]["doppler_shift"]) <= delta_f_limit
        results[sat]["doppler_rate_OK"] = np.abs(results[sat]["doppler_rate"]) <= delta_f_dot_limit
        results[sat]["tolosat_visibility_OK"] = results[sat]["tolosat_angle"] <= semi_angle_limit_tolosat
        results[sat]["iridium_visibility_OK"] = results[sat]["iridium_angle"] <= semi_angle_limit_iridium

        results[sat]["all_OK"] = results[sat]["doppler_shift_OK"] & results[sat]["doppler_rate_OK"] & results[sat][
            "tolosat_visibility_OK"] & results[sat]["iridium_visibility_OK"]

        IRIDIUM_visibility.append(results[sat]["all_OK"].rename(sat))

        if results[sat]["all_OK"].any():
            print(f"{sat} OK")

IRIDIUM_visibility = pd.concat(IRIDIUM_visibility, axis=1)
IRIDIUM_visibility["sum_ok"] = IRIDIUM_visibility.select_dtypes(include=['bool']).sum(axis=1)
results['datetime'] = dt.epoch_to_datetime(results['epochs'])
results["timedelta"] = results["datetime"] - results["datetime"][0]

IRIDIUM_windows = IRIDIUM_visibility.copy()
IRIDIUM_windows["bool"] = IRIDIUM_windows["sum_ok"] > 0

# Code steps from https://joshdevlin.com/blog/calculate-streaks-in-pandas/
IRIDIUM_windows['start_bool'] = IRIDIUM_windows["bool"].ne(IRIDIUM_windows["bool"].shift(1))
IRIDIUM_windows['end_bool'] = IRIDIUM_windows["bool"].ne(IRIDIUM_windows["bool"].shift(-1))
IRIDIUM_windows['streak_id'] = IRIDIUM_windows['start_bool'].cumsum()

IRIDIUM_windows.loc[IRIDIUM_windows['start_bool'], 'start'] = IRIDIUM_windows['epochs']
IRIDIUM_windows['start'] = IRIDIUM_windows['start'].fillna(method="ffill")
IRIDIUM_windows = IRIDIUM_windows[IRIDIUM_windows['end_bool']]
IRIDIUM_windows = IRIDIUM_windows.rename({
    "epochs": "end",
    "bool": "eclipse"
}, axis=1)
IRIDIUM_windows = IRIDIUM_windows[["eclipse", "start", "end"]]
IRIDIUM_windows = IRIDIUM_windows[IRIDIUM_windows['eclipse']].drop("eclipse", axis=1)
IRIDIUM_windows['duration'] = IRIDIUM_windows['end'] - IRIDIUM_windows['start']
IRIDIUM_windows = IRIDIUM_windows.reset_index(drop=True)

print("Done")
