import numpy as np
import pandas as pd
from tqdm import tqdm

from attitude.sun_pointing_rotation import compute_body_vectors
from results_processing import get_list_of_contents, get_results_dict
from useful_functions import date_transformations as dt
from useful_functions import get_spacecraft
from useful_functions.constants import SPEED_OF_LIGHT

Tolosat = get_spacecraft("Tolosat")
Iridium = get_spacecraft("Iridium")

f0 = 1621.25e6  # H
delta_f_limit = 37500  # Hz doppler shift max +/-
delta_f_dot_limit = 350  # 375 # Hz/s doppler rate max +/-
semi_angle_limit_tolosat = Tolosat[
    "iridium_antenna_half_angle"
]  # deg semi-angle visibility
semi_angle_limit_iridium = Iridium["antenna_half_angle"]  # deg semi-angle visibility
iridium_antennas_location = "pmX"  # "pmX" or "pmY"

selected_iridium = "IRIDIUM 100"

selected_iridium_nospace = selected_iridium.replace(" ", "_")


# pointage zenith // pointage soleil ??


def compute_doppler_visibility(results_dict):
    sun_directions = results_dict["sun_direction"].to_numpy()
    epochs = results_dict["epochs"].to_numpy()
    pX_vector, pY_vector, _ = compute_body_vectors(epochs, sun_directions)
    if iridium_antennas_location == "pmX":
        iridium_antenna_1_vector = pX_vector
        iridium_antenna_2_vector = -pX_vector
    elif iridium_antennas_location == "pmY":
        iridium_antenna_1_vector = pY_vector
        iridium_antenna_2_vector = -pY_vector
    else:
        raise ValueError("iridium_antennas_location must be pmX or pmY")
    visibility = [results_dict["epochs"].copy().rename("epochs")]
    sat_results = [results_dict["epochs"].copy().rename("epochs")]
    for sat in tqdm(
        results_dict, ncols=80, desc=f"Satellites", position=1, leave=False
    ):
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
            beta = dv / SPEED_OF_LIGHT
            gamma = 1 / np.sqrt(1 - beta**2)

            results_dict[sat]["doppler_shift"] = f0 * (
                1 / (gamma * (1 + beta * np.cos(theta_r))) - 1
            )
            results_dict[sat]["doppler_rate"] = np.gradient(
                results_dict[sat]["doppler_shift"], results_dict["epochs"]
            )

            tolosat_angle_1 = np.arccos(
                np.sum(relative_position * iridium_antenna_1_vector, axis=1)
                / (
                    np.linalg.norm(relative_position, axis=1)
                    * np.linalg.norm(iridium_antenna_1_vector, axis=1)
                )
            )
            results_dict[sat]["tolosat_angle_1"] = np.rad2deg(tolosat_angle_1)
            tolosat_angle_2 = np.arccos(
                np.sum(relative_position * iridium_antenna_2_vector, axis=1)
                / (
                    np.linalg.norm(relative_position, axis=1)
                    * np.linalg.norm(iridium_antenna_2_vector, axis=1)
                )
            )
            results_dict[sat]["tolosat_angle_2"] = np.rad2deg(tolosat_angle_2)

            iridium_angle = np.arccos(
                np.sum(relative_position * iridium_position, axis=1)
                / (
                    np.linalg.norm(relative_position, axis=1)
                    * np.linalg.norm(iridium_position, axis=1)
                )
            )
            results_dict[sat]["iridium_angle"] = np.rad2deg(iridium_angle)

            results_dict[sat]["doppler_shift_OK"] = (
                np.abs(results_dict[sat]["doppler_shift"]) <= delta_f_limit
            )
            results_dict[sat]["doppler_rate_OK"] = (
                np.abs(results_dict[sat]["doppler_rate"]) <= delta_f_dot_limit
            )
            results_dict[sat]["tolosat_visibility_OK"] = (
                results_dict[sat]["tolosat_angle_1"] <= semi_angle_limit_tolosat
            ) | (results_dict[sat]["tolosat_angle_2"] <= semi_angle_limit_tolosat)
            results_dict[sat]["iridium_visibility_OK"] = (
                results_dict[sat]["iridium_angle"] <= semi_angle_limit_iridium
            )

            results_dict[sat]["all_OK"] = (
                results_dict[sat]["doppler_shift_OK"]
                & results_dict[sat]["doppler_rate_OK"]
                & results_dict[sat]["tolosat_visibility_OK"]
                & results_dict[sat]["iridium_visibility_OK"]
            )

            if sat == selected_iridium:
                sat_results.append(results_dict[sat]["tolosat_angle_1"])
                sat_results.append(results_dict[sat]["tolosat_angle_2"])
                sat_results.append(results_dict[sat]["iridium_angle"])
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
IRIDIUM_visibility = pd.DataFrame(columns=[])
IRIDIUM_windows = pd.DataFrame(columns=[])
IRIDIUM_sat_results = pd.DataFrame(columns=[])

folders = get_list_of_contents("iridium_states")
folders = [int(x) for x in folders]
folders.sort()

print(f"Starting Doppler processing of {len(folders)} datasets...")
for folder in tqdm(folders, ncols=80, desc="Datasets", position=0, leave=True):
    results = get_results_dict(f"iridium_states/{folder}")
    tmp_visibility, tmp_windows, tmp_sat_results = compute_doppler_visibility(results)
    IRIDIUM_visibility = pd.concat(
        [IRIDIUM_visibility, tmp_visibility], ignore_index=True
    )
    IRIDIUM_windows = pd.concat([IRIDIUM_windows, tmp_windows], ignore_index=True)
    IRIDIUM_sat_results = pd.concat(
        [IRIDIUM_sat_results, tmp_sat_results], ignore_index=True
    )

IRIDIUM_sat_results["seconds"] = (
    IRIDIUM_sat_results["epochs"] - IRIDIUM_sat_results["epochs"][0]
)

IRIDIUM_windows = IRIDIUM_windows[IRIDIUM_windows["duration"] > 0]

IRIDIUM_windows["timedelta"] = IRIDIUM_windows["start"] - IRIDIUM_windows["start"][0]
IRIDIUM_windows["seconds"] = IRIDIUM_windows["timedelta"].dt.total_seconds()
IRIDIUM_visibility["seconds"] = (
    IRIDIUM_visibility["epochs"] - IRIDIUM_visibility["epochs"][0]
)
print(f"Minimum IRIDIUM window duration: {IRIDIUM_windows['duration'].min()} seconds")
print(f"Maximum IRIDIUM window duration: {IRIDIUM_windows['duration'].max()} seconds")
print(f"Average IRIDIUM window duration: {IRIDIUM_windows['duration'].mean()} seconds")
print(
    f"Average IRIDIUM passes per day: {len(IRIDIUM_windows) / IRIDIUM_windows['seconds'].max() * 86400:.2f} passes"
)
print(
    f"Average IRIDIUM visibility per day: "
    f"{IRIDIUM_windows['duration'].sum() / IRIDIUM_windows['seconds'].max() * 86400:.2f} seconds"
)

IRIDIUM_visibility.to_csv("results/iridium_visibility.csv")
IRIDIUM_windows.to_csv("results/iridium_windows.csv")

print("Done")
