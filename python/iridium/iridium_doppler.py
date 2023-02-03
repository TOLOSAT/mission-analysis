import numpy as np
import pandas as pd
from tqdm import tqdm

from results_processing import get_list_of_contents, get_results_dict
from useful_functions import date_transformations as dt

c = 299792458  # m/s
f0 = 1621.25e6  # H
delta_f_limit = 37500  # Hz doppler shift max +/-
delta_f_dot_limit = 350  # 375  # Hz/s doppler rate max +/-
semi_angle_limit_tolosat = 30  # deg semi-angle visibility
semi_angle_limit_iridium = 30  # deg semi-angle visibility


# pointage zenith // pointage soleil ??

def compute_doppler_visibility(results_dict):
    zenith = results_dict["Tolosat"][["x", "y", "z"]]
    zenith = zenith / np.linalg.norm(zenith, axis=1)[:, None]
    sat_sun = results_dict["sun_position"] - zenith
    sat_sun = sat_sun / np.linalg.norm(sat_sun, axis=1)[:, None]
    tmp_vector = np.cross(sat_sun, zenith)
    top_pointing = np.cross(tmp_vector, sat_sun)
    visibility = [results_dict["epochs"].copy().rename("epochs")]
    for sat in tqdm(results_dict):
        if "IRIDIUM" not in sat:
            continue
        else:
            iridium_position = results_dict[sat][["x", "y", "z"]].to_numpy()
            dx = (results_dict[sat]["x"] - results_dict["Tolosat"]["x"]).to_numpy()
            dy = (results_dict[sat]["y"] - results_dict["Tolosat"]["y"]).to_numpy()
            dz = (results_dict[sat]["z"] - results_dict["Tolosat"]["z"]).to_numpy()
            results_dict[sat]["dx"] = dx
            results_dict[sat]["dy"] = dy
            results_dict[sat]["dz"] = dz
            relative_position = np.array([dx, dy, dz]).T

            dv_x = (results_dict[sat]["vx"] - results_dict["Tolosat"]["vx"]).to_numpy()
            dv_y = (results_dict[sat]["vy"] - results_dict["Tolosat"]["vy"]).to_numpy()
            dv_z = (results_dict[sat]["vz"] - results_dict["Tolosat"]["vz"]).to_numpy()
            results_dict[sat]["dv_x"] = dv_x
            results_dict[sat]["dv_y"] = dv_y
            results_dict[sat]["dv_z"] = dv_z
            relative_velocity = np.array([dv_x, dv_y, dv_z]).T
            dv = np.sqrt(dv_x ** 2 + dv_y ** 2 + dv_z ** 2)
            results_dict[sat]["dv"] = dv

            theta_r = np.arccos(np.sum(relative_position * relative_velocity, axis=1) / (
                    np.linalg.norm(relative_position, axis=1) * np.linalg.norm(relative_velocity, axis=1)))
            results_dict[sat]["theta_r_deg"] = np.deg2rad(theta_r)
            beta = dv / c
            gamma = 1 / np.sqrt(1 - beta ** 2)

            results_dict[sat]["doppler_shift"] = f0 * (1 / (gamma * (1 + beta * np.cos(theta_r))) - 1)
            results_dict[sat]["doppler_rate"] = np.gradient(results_dict[sat]["doppler_shift"], results_dict["epochs"])

            tolosat_angle = np.arccos(np.sum(relative_position * top_pointing, axis=1) / (
                    np.linalg.norm(relative_position, axis=1) * np.linalg.norm(top_pointing, axis=1)))
            results_dict[sat]["tolosat_angle"] = np.rad2deg(tolosat_angle)

            iridium_angle = np.arccos(np.sum(relative_position * iridium_position, axis=1) / (
                    np.linalg.norm(relative_position, axis=1) * np.linalg.norm(iridium_position, axis=1)))
            results_dict[sat]["iridium_angle"] = np.rad2deg(iridium_angle)

            results_dict[sat]["doppler_shift_OK"] = np.abs(results_dict[sat]["doppler_shift"]) <= delta_f_limit
            results_dict[sat]["doppler_rate_OK"] = np.abs(results_dict[sat]["doppler_rate"]) <= delta_f_dot_limit
            results_dict[sat]["tolosat_visibility_OK"] = results_dict[sat]["tolosat_angle"] <= semi_angle_limit_tolosat
            results_dict[sat]["iridium_visibility_OK"] = results_dict[sat]["iridium_angle"] <= semi_angle_limit_iridium

            results_dict[sat]["all_OK"] = \
                results_dict[sat]["doppler_shift_OK"] & results_dict[sat]["doppler_rate_OK"] & results_dict[sat][
                    "tolosat_visibility_OK"] & results_dict[sat]["iridium_visibility_OK"]

            visibility.append(results_dict[sat]["all_OK"].rename(sat))

            # if results_dict[sat]["all_OK"].any():
            #     print(f"{sat} OK")

    visibility = pd.concat(visibility, axis=1)
    visibility["sum_ok"] = visibility.select_dtypes(include=['bool']).sum(axis=1)
    results_dict['datetime'] = dt.epoch_to_datetime(results_dict['epochs'])
    results_dict["timedelta"] = results_dict["datetime"] - results_dict["datetime"][0]
    windows = visibility.copy()
    visibility = visibility[visibility["sum_ok"] > 0]
    windows["bool"] = windows["sum_ok"] > 0

    # Code steps from https://joshdevlin.com/blog/calculate-streaks-in-pandas/
    windows['start_bool'] = windows["bool"].ne(windows["bool"].shift(1))
    windows['end_bool'] = windows["bool"].ne(windows["bool"].shift(-1))
    windows['streak_id'] = windows['start_bool'].cumsum()

    windows.loc[windows['start_bool'], 'start'] = windows['epochs']
    windows['start'] = windows['start'].fillna(method="ffill")
    windows = windows[windows['end_bool']]
    windows = windows.rename({
        "epochs": "end",
        "bool": "eclipse"
    }, axis=1)
    windows = windows[["eclipse", "start", "end"]]
    windows = windows[windows['eclipse']].drop("eclipse", axis=1)
    windows.rename({"start": "start_epoch", "end": "end_epoch"}, axis=1, inplace=True)
    windows["start"] = dt.epoch_to_datetime(windows["start_epoch"])
    windows["end"] = dt.epoch_to_datetime(windows["end_epoch"])
    windows['duration'] = windows['end_epoch'] - windows['start_epoch']
    windows.drop(["start_epoch", "end_epoch"], axis=1, inplace=True)
    windows = windows.reset_index(drop=True)
    return visibility, windows


# Initialize DataFrames
IRIDIUM_visibility = pd.DataFrame(columns=[])
IRIDIUM_windows = pd.DataFrame(columns=[])

folders = get_list_of_contents("iridium_states")
for folder in folders:
    print(f"Performing Doppler analysis for propagation {folder}...")
    results = get_results_dict(f"iridium_states/{folder}")
    tmp_visibility, tmp_windows = compute_doppler_visibility(results)
    IRIDIUM_visibility = pd.concat([IRIDIUM_visibility, tmp_visibility], ignore_index=True)
    IRIDIUM_windows = pd.concat([IRIDIUM_windows, tmp_windows], ignore_index=True)
IRIDIUM_windows.sort_values(by="start", inplace=True)
IRIDIUM_visibility.sort_values(by="epochs", inplace=True)
print("Done")
