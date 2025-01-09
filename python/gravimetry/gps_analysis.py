'''
from gps_doppler import (
    gps_visibility,
    gps_windows,
    gps_sat_results,
    selected_gps,
    selected_gps_nospace,
)
'''

import pandas as pd
from useful_functions import plot_functions as pf


selected_gps = "GPS BIIR-13 (PRN 02)"
selected_gps_nospace = selected_gps.replace(" ", "_")

gps_visibility_path = 'results/gps_visibility.csv'
gps_windows_path = 'results/gps_windows.csv'
gps_sat_results_path = 'results/gps_sat_results.csv'

gps_visibility = pd.read_csv(gps_visibility_path)
gps_windows = pd.read_csv(gps_windows_path)
gps_sat_results = pd.read_csv(gps_sat_results_path)


fig, axes = pf.dark_figure()
axes[0].plot(gps_sat_results["seconds"] / 86400, gps_sat_results["doppler_shift"] / 1e3)
axes[0].set_title(f"Doppler shift of {selected_gps}")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Doppler shift [kHz]")
axes[0].set_xlim(0, gps_sat_results["seconds"].max() / 86400)
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
