from useful_functions.filter_functions import filter_sat_data
from useful_functions import plot_functions as pf
from useful_functions.date_transformations import epoch_to_datetime
import matplotlib.dates as mdates
import pandas as pd

start_date = '2024-01-08 12:00:00+00:00'
end_date = '2024-01-22 18:00:00+00:00'

selected_gps = "GPS BIIR-13 (PRN 02)"
selected_gps_nospace = selected_gps.replace(" ", "_")

gps_visibility_path = 'results/5days/gps_visibility.csv'
gps_windows_path = 'results/5days/gps_windows.csv'
gps_sat_results_path = 'results/5days/gps_sat_results.csv'

filtered_visibility, filtered_gps_sat_results, filtered_windows = filter_sat_data(gps_visibility_path, gps_windows_path,gps_sat_results_path,start_date, end_date)

filtered_gps_sat_results["datetime"] = epoch_to_datetime(filtered_gps_sat_results["epochs"])
print('Filtered gps_sat_results')
filtered_visibility["datetime"] = epoch_to_datetime(filtered_visibility["epochs"])
print('Filtered visibility')
filtered_windows["start_datetime"] = pd.to_datetime(filtered_windows["start"], utc=True)
print('Filtered windows')

date_format = mdates.DateFormatter('%d-%m-%y\n%H:%M')

fig, axes = pf.dark_figure()
axes[0].plot(filtered_gps_sat_results["datetime"], filtered_gps_sat_results["doppler_shift"] / 1e3)
axes[0].set_title(f"Doppler shift of {selected_gps}")
axes[0].set_ylabel("Doppler shift [kHz]")
axes[0].xaxis.set_major_formatter(date_format)
fig.autofmt_xdate()
for label in axes[0].get_xticklabels():
    label.set_fontsize(8)
pf.finish_dark_figure(
    fig, f"results/filtered_{selected_gps_nospace}_doppler_shift.png", show=True
)

fig, axes = pf.light_figure()
axes[0].plot(filtered_gps_sat_results["datetime"], filtered_gps_sat_results["doppler_shift"] / 1e3)
axes[0].set_title(f"Doppler shift of {selected_gps}")
#axes[0].set_xlabel("Date")
axes[0].set_ylabel("Doppler shift [kHz]")
axes[0].xaxis.set_major_formatter(date_format)
fig.autofmt_xdate()
for label in axes[0].get_xticklabels():
    label.set_fontsize(8)
pf.finish_light_figure(
    fig, f"results/filtered_{selected_gps_nospace}_doppler_shift_light.png", show=True
)

fig, axes = pf.dark_figure()
axes[0].plot(filtered_gps_sat_results["datetime"], filtered_gps_sat_results["doppler_rate"])
axes[0].set_title(f"Doppler rate of {selected_gps}")
#axes[0].set_xlabel("Date")
axes[0].set_ylabel("Doppler rate [Hz/s]")
axes[0].xaxis.set_major_formatter(date_format)
fig.autofmt_xdate()
for label in axes[0].get_xticklabels():
    label.set_fontsize(8)
pf.finish_dark_figure(
    fig, f"results/filtered_{selected_gps_nospace}_doppler_rate.png", show=True
)

fig, axes = pf.light_figure()
axes[0].plot(filtered_gps_sat_results["datetime"], filtered_gps_sat_results["doppler_rate"])
axes[0].set_title(f"Doppler rate of {selected_gps}")
#axes[0].set_xlabel("Date")
axes[0].set_ylabel("Doppler rate [Hz/s]")
axes[0].xaxis.set_major_formatter(date_format)
fig.autofmt_xdate()
for label in axes[0].get_xticklabels():
    label.set_fontsize(8)
pf.finish_light_figure(
    fig, f"results/filtered_{selected_gps_nospace}_doppler_rate_light.png", show=True
)

fig, axes = pf.dark_figure()
axes[0].plot(
    filtered_visibility["datetime"],
    filtered_visibility["sum_ok"],
    linestyle="none",
    marker=".",
)
axes[0].set_title("Visibility of gps satellites satisfying all 4 conditions")
#axes[0].set_xlabel("Date")
axes[0].set_ylabel("Number of satellites [-]")
axes[0].xaxis.set_major_formatter(date_format)
fig.autofmt_xdate()
for label in axes[0].get_xticklabels():
    label.set_fontsize(8)
pf.finish_dark_figure(fig, "results/filtered_gps_visibility.png", show=True, force_y_int=True)

fig, axes = pf.light_figure()
axes[0].plot(
    filtered_visibility["datetime"],
    filtered_visibility["sum_ok"],
    linestyle="none",
    marker=".",
)
axes[0].set_title("Visibility of gps satellites satisfying all 4 conditions")
#axes[0].set_xlabel("Date")
axes[0].set_ylabel("Number of satellites [-]")
axes[0].xaxis.set_major_formatter(date_format)
fig.autofmt_xdate()
for label in axes[0].get_xticklabels():
    label.set_fontsize(8)
pf.finish_light_figure(
    fig, "results/filtered_gps_visibility_light.png", show=True, force_y_int=True
)

fig, axes = pf.dark_figure()
axes[0].vlines(filtered_windows["start_datetime"], 0, filtered_windows["duration"] / 60)
axes[0].set_title("Visibility windows of at least one gps satellite")
#axes[0].set_xlabel("Date")
axes[0].set_ylabel("Window duration [mins]")
axes[0].set_ylim(0, filtered_windows["duration"].max() / 60)
axes[0].xaxis.set_major_formatter(date_format)
fig.autofmt_xdate()
for label in axes[0].get_xticklabels():
    label.set_fontsize(8)
pf.finish_dark_figure(fig, "results/filtered_gps_windows.png", show=True)

fig, axes = pf.light_figure()
axes[0].vlines(filtered_windows["start_datetime"], 0, filtered_windows["duration"] / 60)
axes[0].set_title("Visibility windows of at least one gps satellite")
#axes[0].set_xlabel("Date")
axes[0].set_ylabel("Window duration [mins]")
axes[0].set_ylim(0, filtered_windows["duration"].max() / 60)
axes[0].xaxis.set_major_formatter(date_format)
fig.autofmt_xdate()
for label in axes[0].get_xticklabels():
    label.set_fontsize(8)
pf.finish_light_figure(fig, "results/filtered_gps_windows_light.png", show=True)



