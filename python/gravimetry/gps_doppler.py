import numpy as np
import pandas as pd
from tqdm import tqdm

from results_processing import get_list_of_contents, get_results_dict
from useful_functions import date_transformations as dt
from attitude.sun_pointing_rotation import compute_body_vectors

c = 299792458  # m/s
f0 = 1621.25e6  # H
delta_f_limit = 37500  # Hz doppler shift max +/-
delta_f_dot_limit = 350  # 375 # Hz/s doppler rate max +/-
semi_angle_limit_tolosat = 60  # deg semi-angle visibility
semi_angle_limit_gps = 30  # deg semi-angle visibility
gps_antennas_location = "pmY"  # "pmX" or "pmY"

selected_gps = "GPS BIIR-13 (PRN 02)"

selected_gps_nospace = selected_gps.replace(" ", "_")


# pointage zenith // pointage soleil ??


def compute_doppler_visibility(results_dict):
    sun_directions = results_dict["sun_direction"].to_numpy()
    epochs = results_dict["epochs"].to_numpy()
    pX_vector, pY_vector, _ = compute_body_vectors(epochs, sun_directions)
    if gps_antennas_location == "pmX":
        gps_antenna_1_vector = pX_vector
        gps_antenna_2_vector = -pX_vector
    elif gps_antennas_location == "pmY":
        gps_antenna_1_vector = pY_vector
        gps_antenna_2_vector = -pY_vector
    else:
        raise ValueError("gps_antennas_location must be pmX or pmY")
    visibility = [results_dict["epochs"].copy().rename("epochs")]
    sat_results = [results_dict["epochs"].copy().rename("epochs")]
    for sat in tqdm(
        results_dict, ncols=80, desc=f"Satellites", position=1, leave=False
    ):
        if "GPS" not in sat:
            continue
        else:
            gps_position = results_dict[sat][["x", "y", "z"]].to_numpy()
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
            dv = np.sqrt(dv_x**2 + dv_y**2 + dv_z**2)
            results_dict[sat]["dv"] = dv

            theta_r = np.arccos(
                np.sum(relative_position * relative_velocity, axis=1)
                / (
                    np.linalg.norm(relative_position, axis=1)
                    * np.linalg.norm(relative_velocity, axis=1)
                )
            )
            results_dict[sat]["theta_r_deg"] = np.deg2rad(theta_r)
            beta = dv / c
            gamma = 1 / np.sqrt(1 - beta**2)

            results_dict[sat]["doppler_shift"] = f0 * (
                1 / (gamma * (1 + beta * np.cos(theta_r))) - 1
            )
            results_dict[sat]["doppler_rate"] = np.gradient(
                results_dict[sat]["doppler_shift"], results_dict["epochs"]
            )

            tolosat_angle_1 = np.arccos(
                np.sum(relative_position * gps_antenna_1_vector, axis=1)
                / (
                    np.linalg.norm(relative_position, axis=1)
                    * np.linalg.norm(gps_antenna_1_vector, axis=1)
                )
            )
            results_dict[sat]["tolosat_angle_1"] = np.rad2deg(tolosat_angle_1)
            tolosat_angle_2 = np.arccos(
                np.sum(relative_position * gps_antenna_2_vector, axis=1)
                / (
                    np.linalg.norm(relative_position, axis=1)
                    * np.linalg.norm(gps_antenna_2_vector, axis=1)
                )
            )
            results_dict[sat]["tolosat_angle_2"] = np.rad2deg(tolosat_angle_2)

            gps_angle = np.arccos(
                np.sum(relative_position * gps_position, axis=1)
                / (
                    np.linalg.norm(relative_position, axis=1)
                    * np.linalg.norm(gps_position, axis=1)
                )
            )
            results_dict[sat]["gps_angle"] = np.rad2deg(gps_angle)

            results_dict[sat]["doppler_shift_OK"] = (
                np.abs(results_dict[sat]["doppler_shift"]) <= delta_f_limit
            )
            results_dict[sat]["doppler_rate_OK"] = (
                np.abs(results_dict[sat]["doppler_rate"]) <= delta_f_dot_limit
            )
            results_dict[sat]["tolosat_visibility_OK"] = (
                results_dict[sat]["tolosat_angle_1"] <= semi_angle_limit_tolosat
            ) | (results_dict[sat]["tolosat_angle_2"] <= semi_angle_limit_tolosat)
            results_dict[sat]["gps_visibility_OK"] = (
                results_dict[sat]["gps_angle"] <= semi_angle_limit_gps
            )

            results_dict[sat]["all_OK"] = (
                results_dict[sat]["doppler_shift_OK"]
                & results_dict[sat]["doppler_rate_OK"]
                & results_dict[sat]["tolosat_visibility_OK"]
                & results_dict[sat]["gps_visibility_OK"]
            )

            if sat == selected_gps:
                sat_results.append(results_dict[sat]["tolosat_angle_1"])
                sat_results.append(results_dict[sat]["tolosat_angle_2"])
                sat_results.append(results_dict[sat]["gps_angle"])
                sat_results.append(results_dict[sat]["doppler_shift"])
                sat_results.append(results_dict[sat]["doppler_rate"])
            visibility.append(results_dict[sat]["all_OK"].rename(sat))

            # if results_dict[sat]["all_OK"].any():
            #     print(f"{sat} OK")
    sat_results = pd.concat(sat_results, axis=1)
    visibility = pd.concat(visibility, axis=1)
    visibility["sum_ok"] = visibility.select_dtypes(include=["bool"]).sum(axis=1)
    results_dict["datetime"] = dt.epoch_to_datetime(results_dict["epochs"])
    results_dict["timedelta"] = results_dict["datetime"] - results_dict["datetime"][0]
    windows = visibility.copy()
    visibility = visibility[visibility["sum_ok"] > 0]
    windows["bool"] = windows["sum_ok"] > 0

    # Code steps from https://joshdevlin.com/blog/calculate-streaks-in-pandas/
    windows["start_bool"] = windows["bool"].ne(windows["bool"].shift(1))
    windows["end_bool"] = windows["bool"].ne(windows["bool"].shift(-1))
    windows["streak_id"] = windows["start_bool"].cumsum()

    windows.loc[windows["start_bool"], "start"] = windows["epochs"]
    windows["start"] = windows["start"].fillna(method="ffill")
    windows = windows[windows["end_bool"]]
    windows = windows.rename({"epochs": "end", "bool": "eclipse"}, axis=1)
    windows = windows[["eclipse", "start", "end"]]
    windows = windows[windows["eclipse"]].drop("eclipse", axis=1)
    windows.rename({"start": "start_epoch", "end": "end_epoch"}, axis=1, inplace=True)
    windows["start"] = dt.epoch_to_datetime(windows["start_epoch"])
    windows["end"] = dt.epoch_to_datetime(windows["end_epoch"])
    windows["duration"] = windows["end_epoch"] - windows["start_epoch"]
    windows.drop(["start_epoch", "end_epoch"], axis=1, inplace=True)
    windows = windows.reset_index(drop=True)
    return visibility, windows, sat_results


# Initialize DataFrames
gps_visibility = pd.DataFrame(columns=[])
gps_windows = pd.DataFrame(columns=[])
gps_sat_results = pd.DataFrame(columns=[])

folders = get_list_of_contents("gps_states")
folders = [int(x) for x in folders]
folders.sort()

print(f"Starting Doppler processing of {len(folders)} datasets...")
for folder in tqdm(folders, ncols=80, desc="Datasets", position=0, leave=True):
    results = get_results_dict(f"gps_states/{folder}")
    tmp_visibility, tmp_windows, tmp_sat_results = compute_doppler_visibility(results)
    gps_visibility = pd.concat([gps_visibility, tmp_visibility], ignore_index=True)
    gps_windows = pd.concat([gps_windows, tmp_windows], ignore_index=True)
    gps_sat_results = pd.concat([gps_sat_results, tmp_sat_results], ignore_index=True)

gps_sat_results["seconds"] = gps_sat_results["epochs"] - gps_sat_results["epochs"][0]

gps_windows = gps_windows[gps_windows["duration"] > 0]

gps_windows["timedelta"] = gps_windows["start"] - gps_windows["start"][0]
gps_windows["seconds"] = gps_windows["timedelta"].dt.total_seconds()
gps_visibility["seconds"] = gps_visibility["epochs"] - gps_visibility["epochs"][0]
print(f"Minimum gps window duration: {gps_windows['duration'].min()} seconds")
print(f"Maximum gps window duration: {gps_windows['duration'].max()} seconds")
print(f"Average gps window duration: {gps_windows['duration'].mean()} seconds")
print(
    f"Average gps passes per day: {len(gps_windows) / gps_windows['seconds'].max() * 86400:.2f} passes"
)
print(
    f"Average gps visibility per day: "
    f"{gps_windows['duration'].sum() / gps_windows['seconds'].max() * 86400:.2f} seconds"
)

gps_visibility.to_csv("results/gps_visibility.csv")
gps_windows.to_csv("results/gps_windows.csv")

print("Done")
