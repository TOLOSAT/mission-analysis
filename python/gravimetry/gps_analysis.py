from datetime import datetime

from gps_doppler import (
    gps_visibility,
    gps_windows,
    gps_sat_results,
    selected_gps,
    selected_gps_nospace,
)

from useful_functions import plot_functions as pf
from useful_functions import datetime_to_epoch
from useful_functions.get_input_data import get_dates

import pandas as pd

desired_start_date = "2024-01-02-13:00:00"
desired_start_time = "13:00:00"
desired_end_date = "2024-01-03"
desired_end_time = "13:00:00"

dates_name = "test"

# Create a window of time to analyze
dates = get_dates(dates_name)

window_start_seconds = datetime_to_epoch(dates["start_date"])
window_end_seconds = datetime_to_epoch(dates["end_date"])

# Find the index of the window that contains the desired time
window_index_start = gps_sat_results["epochs"].searchsorted(window_start_seconds)
window_index_end = gps_sat_results["epochs"].searchsorted(window_end_seconds)

gps_sat_results_window = pd.DataFrame(columns=[])

gps_sat_results_window = gps_sat_results.iloc[window_index_start:window_index_end]

fig, axes = pf.dark_figure()
axes[0].plot(gps_sat_results_window["seconds"] / 86400, gps_sat_results_window["doppler_shift"] / 1e3)
axes[0].set_title(f"Doppler shift of {selected_gps}")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Doppler shift [kHz]")
axes[0].set_xlim(window_start_seconds / 86400, window_end_seconds / 86400)
pf.finish_dark_figure(
    fig, f"results/{selected_gps_nospace}_doppler_shift.png", show=True
)

fig, axes = pf.light_figure()
axes[0].plot(gps_sat_results["seconds"] / 86400, gps_sat_results["doppler_shift"] / 1e3)
axes[0].set_title(f"Doppler shift of {selected_gps}")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Doppler shift [kHz]")
axes[0].set_xlim(0, gps_sat_results["seconds"].max() / 86400)
pf.finish_light_figure(
    fig, f"results/{selected_gps_nospace}_doppler_shift_light.png", show=True
)

fig, axes = pf.dark_figure()
axes[0].plot(gps_sat_results["seconds"] / 86400, gps_sat_results["doppler_rate"])
axes[0].set_title(f"Doppler rate of {selected_gps}")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Doppler rate [Hz/s]")
axes[0].set_xlim(0, gps_sat_results["seconds"].max() / 86400)
pf.finish_dark_figure(
    fig, f"results/{selected_gps_nospace}_doppler_rate.png", show=True
)

fig, axes = pf.light_figure()
axes[0].plot(gps_sat_results["seconds"] / 86400, gps_sat_results["doppler_rate"])
axes[0].set_title(f"Doppler rate of {selected_gps}")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Doppler rate [Hz/s]")
axes[0].set_xlim(0, gps_sat_results["seconds"].max() / 86400)
pf.finish_light_figure(
    fig, f"results/{selected_gps_nospace}_doppler_rate_light.png", show=True
)

fig, axes = pf.dark_figure()
axes[0].plot(
    gps_visibility["seconds"] / 86400,
    gps_visibility["sum_ok"],
    linestyle="none",
    marker=".",
)
axes[0].set_title("Visibility of gps satellites satisfying all 4 conditions")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Number of satellites [-]")
axes[0].set_xlim(0, gps_visibility["seconds"].max() / 86400)
pf.finish_dark_figure(fig, "results/gps_visibility.png", show=True, force_y_int=True)

fig, axes = pf.light_figure()
axes[0].plot(
    gps_visibility["seconds"] / 86400,
    gps_visibility["sum_ok"],
    linestyle="none",
    marker=".",
)
axes[0].set_title("Visibility of gps satellites satisfying all 4 conditions")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Number of satellites [-]")
axes[0].set_xlim(0, gps_visibility["seconds"].max() / 86400)
pf.finish_light_figure(
    fig, "results/gps_visibility_light.png", show=True, force_y_int=True
)

fig, axes = pf.dark_figure()
axes[0].vlines(gps_windows["seconds"] / 86400, 0, gps_windows["duration"] / 60)
axes[0].set_title("Visibility windows of at least one gps satellite")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Window duration [mins]")
axes[0].set_ylim(0, gps_windows["duration"].max() / 60)
axes[0].set_xlim(0, gps_windows["seconds"].max() / 86400)
pf.finish_dark_figure(fig, "results/gps_windows.png", show=True)

fig, axes = pf.light_figure()
axes[0].vlines(gps_windows["seconds"] / 86400, 0, gps_windows["duration"] / 60)
axes[0].set_title("Visibility windows of at least one gps satellite")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Window duration [mins]")
axes[0].set_ylim(0, gps_windows["duration"].max() / 60)
axes[0].set_xlim(0, gps_windows["seconds"].max() / 86400)
pf.finish_light_figure(fig, "results/gps_windows_light.png", show=True)
