from math import log10
import numpy as np
import pandas as pd
from tqdm import tqdm

from attitude.sun_pointing_rotation import compute_body_vectors
from results_processing import get_list_of_contents, get_results_dict
from useful_functions import date_transformations as dt
from useful_functions import get_station
from useful_functions import get_spacecraft
from useful_functions.constants import SPEED_OF_LIGHT

Tolosat = get_spacecraft("Tolosat")
Toulouse_GS = get_station("toulouse")

f0 = 1621.25e6  # Hz
delta_f_limit = 37500  # Hz doppler shift max +/-
delta_f_dot_limit = 350  # 375 # Hz/s doppler rate max +/-
max_distance = 20000e3  # [m] max distance to establish communication with gps satellite
semi_angle_limit_tolosat = Tolosat[
    "gps_antenna_half_angle"
]  # deg semi-angle visibility
semi_angle_limit_GS = Toulouse_GS["antenna_half_angle"]  # deg semi-angle visibility
GS_antennas_location = "pmZ"  # "pmX" or "pmY" or "pmZ"

# pointage zenith // pointage soleil ??


def compute_GS_visibility(results_dict):
    sun_directions = results_dict["sun_direction"].to_numpy()
    epochs = results_dict["epochs"].to_numpy()
    pX_vector, pY_vector, pZ_vector = compute_body_vectors(epochs, sun_directions)
    if GS_antennas_location == "pmX":
        GS_antenna_1_vector = pX_vector
        GS_antenna_2_vector = -pX_vector
    elif GS_antennas_location == "pmY":
        GS_antenna_1_vector = pY_vector
        GS_antenna_2_vector = -pY_vector
    elif GS_antennas_location == "pmZ":
        GS_antenna_1_vector = pZ_vector
        GS_antenna_2_vector = None
    else:
        raise ValueError("GS_antennas_location must be pmX or pmY or pmZ")
    visibility = [results_dict["epochs"].copy().rename("epochs")]
    sat_results = [results_dict["epochs"].copy().rename("epochs")]

    GS_lat = Toulouse_GS["latitude"]
    GS_long = Toulouse_GS["longitude"]
    GS_alt = Toulouse_GS["altitude"]




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
            beta = dv / SPEED_OF_LIGHT
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

            dist = np.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
            results_dict[sat]["distance_OK"] = (
                    computelinkbudg('uplink',dist, 'typical')
            )

            results_dict[sat]["all_OK"] = (
                results_dict[sat]["doppler_shift_OK"]
                & results_dict[sat]["doppler_rate_OK"]
                & results_dict[sat]["tolosat_visibility_OK"]
                & results_dict[sat]["gps_visibility_OK"]
                & results_dict[sat]["distance_OK"]
            )

            if sat == selected_gps:
                sat_results.append(results_dict[sat]["tolosat_angle_1"])
                sat_results.append(results_dict[sat]["tolosat_angle_2"])
                sat_results.append(results_dict[sat]["gps_angle"])
                sat_results.append(results_dict[sat]["doppler_shift"])
                sat_results.append(results_dict[sat]["doppler_rate"])
            visibility.append(results_dict[sat]["all_OK"].rename(sat))

        if results_dict[sat]["all_OK"].any():
            print(f"{sat} OK")

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





# LINK BUDGET PROVIDED BY THE TELEMETRY SUBSYSTEM
def can_communicate_s_band(direction="downlink", distance=1200, case="typical"):
    """Computes the link budget of Tolosat. Parameters are:\n
    direction (uplink or downlink), distance (in km), and case (typical or worst).\n
    Returns 1 if communication can occur.\n
    Returns 0 if communication can't occur.\n
    Returns -1 in case of error."""
    # Direction : "uplink" or "downlink"
    # Elevation : between 0 (horizon) to 90 (straight vertical) degrees
    # Distance : distance in kilometers between groundstation and satellite
    # Case : "worst", "typical"

    if direction == "uplink":
        # Groundstation parameters
        eirp = 54   # dBW

        # Propagation parameters
        frequency = 2.0675  # GHz
        free_space_losses = 20 * (log10(distance) + log10(frequency)) + 92.45   # dB
        if case == "typical":
            atmospheric_losses = 0.04   # dB
            polarization_losses = 0.8   # dB
        elif case == "worst":
            atmospheric_losses = 0.05   # dB
            polarization_losses = 2     # dB
        else:
            return -1
        propagation_losses = free_space_losses + atmospheric_losses + polarization_losses   # dB

        # Satellite hardware parameters
        if case == "typical":
            gain = 3    # dBi
            reflection_coefficient = -19    # dB
            circuit_losses = 4  # dB
        elif case == "worst":
            gain = -7   # dBi
            reflection_coefficient = -18    # dB
            circuit_losses = 6  # dB
        else:
            return -1
        missmatch_losses = -10 * log10(1 - 1 / (10 ** (-reflection_coefficient / 10)))  # dB
        sensitivity = -101.9    # dBm

        # Budget computation
        received_power = eirp + 30 - propagation_losses + gain - missmatch_losses - circuit_losses  # dBm
        margin = received_power - sensitivity   # dB

    elif direction == "downlink":
        # Satellite hardware parameters
        if case == "typical":
            transmission_power = 3  # dBW
            circuit_losses = 4  # dB
            gain = 3    # dBi
            reflection_coefficient = -17    # dB
        elif case == "worst":
            transmission_power = 0  # dBW
            circuit_losses = 6  # dB
            gain = -7   # dBi
            reflection_coefficient = -15    # dB
        else:
            return -1
        missmatch_losses = -10 * log10(1 - 1 / (10 ** (-reflection_coefficient / 10)))  # dB
        eirp = transmission_power - circuit_losses - missmatch_losses + gain    # dBW

        # Propagation parameters
        frequency = 2.245   # GHz
        free_space_losses = 20 * (log10(distance) + log10(frequency)) + 92.45   # dB
        if case == "typical":
            atmospheric_losses = 0.04   # dB
            polarization_losses = 0.8   # dB
        elif case == "worst":
            atmospheric_losses = 0.05   # dB
            polarization_losses = 2     # dB
        else:
            return -1
        propagation_losses = free_space_losses + atmospheric_losses + polarization_losses   # dB

        # Groundstation parameters
        g_over_t = 17   # dB/K
        received_power = eirp + 30 - propagation_losses # dBm
        c_over_n0 = g_over_t + received_power - 10 * log10(1.380649E-23)    # dB
        if case == "typical":
            demodulator_losses = 3  # dB
        elif case == "worst":
            demodulator_losses = 4  # dB
        else:
            return -1
        bitrate = 1000  # kbit/s
        received_eb_over_n0 = c_over_n0 - demodulator_losses - 10 * log10(1000 * bitrate)   # dB
        required_eb_over_n0 = 9.09  # dB
        margin = received_eb_over_n0 - required_eb_over_n0  # dB
    else:
        return -1
    print(margin)
    if margin > 8:  # dB, High margin necessary due to uncertainty on components
        return 1
    else:
        return 0