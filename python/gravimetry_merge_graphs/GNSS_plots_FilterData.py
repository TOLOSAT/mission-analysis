import pandas as pd
import matplotlib.dates as mdates
from useful_functions import plot_functions as pf
from useful_functions.date_transformations import epoch_to_datetime


def plots_filtered_data(flag, start_date, end_date):
    """
    Generates merged plots for GPS, Galileo, and Glonass filtered data based on the selected flag.

    Args:
        flag (int): Defines which constellations to merge:
            1 - GPS & Galileo
            2 - GPS & Glonass
            3 - Galileo & Glonass
            4 - GPS, Galileo & Glonass
        start_date (str): Start date in format 'YYYY-MM-DD HH:MM:SS+00:00'.
        end_date (str): End date in format 'YYYY-MM-DD HH:MM:SS+00:00'.
    """

    # Convert start_date and end_date to filename format
    start_date_filename = start_date[:10].replace('-', '')
    end_date_filename = end_date[:10].replace('-', '')

    # Construct filenames dynamically
    gps_file = f"../gravimetry/results/filtered_sat_results_{start_date_filename}_to_{end_date_filename}.csv"
    galileo_file = f"../gravimetry_galileo/results/filtered_sat_results_{start_date_filename}_to_{end_date_filename}.csv"
    glonass_file = f"../gravimetry_glonass/results/filtered_sat_results_{start_date_filename}_to_{end_date_filename}.csv"

    visibility_gps_file = f"../gravimetry/results/filtered_visibility_{start_date_filename}_to_{end_date_filename}.csv"
    visibility_galileo_file = f"../gravimetry_galileo/results/filtered_visibility_{start_date_filename}_to_{end_date_filename}.csv"
    visibility_glonass_file = f"../gravimetry_glonass/results/filtered_visibility_{start_date_filename}_to_{end_date_filename}.csv"

    windows_gps_file = f"../gravimetry/results/filtered_windows_{start_date_filename}_to_{end_date_filename}.csv"
    windows_galileo_file = f"../gravimetry_galileo/results/filtered_windows_{start_date_filename}_to_{end_date_filename}.csv"
    windows_glonass_file = f"../gravimetry_glonass/results/filtered_windows_{start_date_filename}_to_{end_date_filename}.csv"

    # Read filtered CSVs
    gps_sat_results = pd.read_csv(gps_file) if flag in [1, 2, 4] else None
    galileo_sat_results = pd.read_csv(galileo_file) if flag in [1, 3, 4] else None
    glonass_sat_results = pd.read_csv(glonass_file) if flag in [2, 3, 4] else None

    gps_visibility = pd.read_csv(visibility_gps_file) if flag in [1, 2, 4] else None
    galileo_visibility = pd.read_csv(visibility_galileo_file) if flag in [1, 3, 4] else None
    glonass_visibility = pd.read_csv(visibility_glonass_file) if flag in [2, 3, 4] else None

    gps_windows = pd.read_csv(windows_gps_file) if flag in [1, 2, 4] else None
    galileo_windows = pd.read_csv(windows_galileo_file) if flag in [1, 3, 4] else None
    glonass_windows = pd.read_csv(windows_glonass_file) if flag in [2, 3, 4] else None

    # Convert epochs to datetime
    if gps_sat_results is not None:
        gps_sat_results["datetime"] = epoch_to_datetime(gps_sat_results["epochs"])
    if galileo_sat_results is not None:
        galileo_sat_results["datetime"] = epoch_to_datetime(galileo_sat_results["epochs"])
    if glonass_sat_results is not None:
        glonass_sat_results["datetime"] = epoch_to_datetime(glonass_sat_results["epochs"])

    if gps_visibility is not None:
        gps_visibility["datetime"] = epoch_to_datetime(gps_visibility["epochs"])
    if galileo_visibility is not None:
        galileo_visibility["datetime"] = epoch_to_datetime(galileo_visibility["epochs"])
    if glonass_visibility is not None:
        glonass_visibility["datetime"] = epoch_to_datetime(glonass_visibility["epochs"])

    if gps_windows is not None:
        gps_windows["start_datetime"] = pd.to_datetime(gps_windows["start"], utc=True)
    if galileo_windows is not None:
        galileo_windows["start_datetime"] = pd.to_datetime(galileo_windows["start"], utc=True)
    if glonass_windows is not None:
        glonass_windows["start_datetime"] = pd.to_datetime(glonass_windows["start"], utc=True)

    # Merge selected datasets
    combined_sat_results = pd.concat(filter(None, [gps_sat_results, galileo_sat_results, glonass_sat_results]),
                                     ignore_index=True)
    combined_visibility = pd.concat(filter(None, [gps_visibility, galileo_visibility, glonass_visibility]),
                                    ignore_index=True)
    combined_windows = pd.concat(filter(None, [gps_windows, galileo_windows, glonass_windows]), ignore_index=True)

    # Formatting for plots
    date_format = mdates.DateFormatter('%d-%m-%y\n%H:%M')

    # === Doppler Shift Plot ===
    fig, axes = pf.dark_figure()
    axes[0].plot(combined_sat_results["datetime"], combined_sat_results["doppler_shift"] / 1e3)
    axes[0].set_title("Doppler Shift of Selected GNSS Constellations")
    axes[0].set_ylabel("Doppler shift [kHz]")
    axes[0].xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()
    pf.finish_dark_figure(fig, f"results/filtered_doppler_shift_flag{flag}.png", show=True)

    # === Doppler Rate Plot ===
    fig, axes = pf.dark_figure()
    axes[0].plot(combined_sat_results["datetime"], combined_sat_results["doppler_rate"])
    axes[0].set_title("Doppler Rate of Selected GNSS Constellations")
    axes[0].set_ylabel("Doppler rate [Hz/s]")
    axes[0].xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()
    pf.finish_dark_figure(fig, f"results/filtered_doppler_rate_flag{flag}.png", show=True)

    # === Visibility Plot ===
    fig, axes = pf.dark_figure()
    axes[0].plot(combined_visibility["datetime"], combined_visibility["sum_ok"], linestyle="none", marker=".")
    axes[0].set_title("Visibility of Selected GNSS Satellites")
    axes[0].set_ylabel("Number of satellites [-]")
    axes[0].xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()
    pf.finish_dark_figure(fig, f"results/filtered_visibility_flag{flag}.png", show=True, force_y_int=True)

    # === Visibility Windows Plot ===
    fig, axes = pf.dark_figure()
    axes[0].vlines(combined_windows["start_datetime"], 0, combined_windows["duration"] / 60)
    axes[0].set_title("Visibility Windows of Selected GNSS Satellites")
    axes[0].set_ylabel("Window duration [mins]")
    axes[0].set_ylim(0, combined_windows["duration"].max() / 60)
    axes[0].xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()
    pf.finish_dark_figure(fig, f"results/filtered_windows_flag{flag}.png", show=True)


# === Run the function with selected flag ===
start_date = '2024-01-05 12:00:00+00:00'
end_date = '2024-01-20 18:00:00+00:00'
flag = 1  # Change this to choose which constellations to merge (1, 2, 3, or 4)
plots_filtered_data(flag, start_date, end_date)
