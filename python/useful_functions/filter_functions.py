from datetime import datetime as dt, timezone
from useful_functions.date_transformations import datetime_to_epoch
import pandas as pd
from astropy.time import Time

def filter_gps_data(gps_visibility_path, gps_windows_path, gps_sat_results_path, start_date, end_date):
    """
    Filter GPS visibility data for a specified date range and save the results.

    Parameters
    ----------
    gps_visibility_path: str
        path to the GPS visibility CSV file.
    start_date: str
        start date in 'YYYY-MM-DD-HH:MM:SS' format.
    end_date: str
        end date in 'YYYY-MM-DD-HH:MM:SS' format.
    """

    # Parse start and end dates
    start_datetime = dt.strptime(start_date, "%Y-%m-%d %H:%M:%S+00:00").replace(tzinfo=timezone.utc)
    end_datetime = dt.strptime(end_date, "%Y-%m-%d %H:%M:%S+00:00").replace(tzinfo=timezone.utc)

    start_epoch = datetime_to_epoch(start_datetime)
    end_epoch = datetime_to_epoch(end_datetime)

    # Filter GPS visibility data
    try:
        gps_visibility = pd.read_csv(gps_visibility_path)
    except FileNotFoundError:
        print(f"Error: File not found at {gps_visibility_path}.")
        return None

    filtered_visibility = gps_visibility[
        (gps_visibility['epochs'] >= start_epoch) & (gps_visibility['epochs'] <= end_epoch)
        ]

    # Filter GPS_sat_results data
    try:
        gps_sat_results = pd.read_csv(gps_sat_results_path)
    except FileNotFoundError:
        print(f"Error: File not found at {gps_sat_results_path}.")
        return None

    filtered_gps_sat_results = gps_sat_results[
        (gps_sat_results['epochs'] >= start_epoch) & (gps_sat_results['epochs'] <= end_epoch)
        ]

    # Filter GPS windows data
    try:
        gps_windows = pd.read_csv(gps_windows_path)
    except FileNotFoundError:
        print(f"Error: File not found at {gps_windows_path}.")
        return None

    start_j2000, startfile_j2000 = iso_to_J2000(start_date, gps_windows, 'start')
    end_j2000, endfile_j2000 = iso_to_J2000(end_date, gps_windows, 'end')

    filtered_windows = gps_windows[
        (endfile_j2000 >= start_j2000) & ((endfile_j2000 <= end_j2000) | (startfile_j2000 < end_j2000))]

    start_str = start_datetime.strftime('%Y%m%d')
    end_str = end_datetime.strftime('%Y%m%d')

    output_filename_visibility = f'results/filtered_gps_visibility_{start_str}_to_{end_str}.csv'
    filtered_visibility.to_csv(output_filename_visibility)

    output_filename_sat_results = f'results/filtered_gps_sat_results_{start_str}_to_{end_str}.csv'
    filtered_gps_sat_results.to_csv(output_filename_sat_results)

    output_filename_windows = f'results/filtered_gps_windows_{start_str}_to_{end_str}.csv'
    filtered_windows.to_csv(output_filename_windows)

    print(f'Data saved for range {start_date} to {end_date}.')

    return filtered_visibility, filtered_gps_sat_results, filtered_windows


def iso_to_J2000(date, gps_windows, str_label):
    ISO_datetime = dt.fromisoformat(date)
    formatted_ISO = ISO_datetime.strftime('%Y-%m-%dT%H:%M:%S')

    formatted_file_dt = [
        dt.fromisoformat(file_dt).strftime('%Y-%m-%dT%H:%M:%S')
        for file_dt in gps_windows[str_label]
    ]

    date_j200 = Time(formatted_ISO, format='isot', scale='utc').jyear
    date_file_j200 = Time(formatted_file_dt, format='isot', scale='utc').jyear

    return date_j200, date_file_j200

