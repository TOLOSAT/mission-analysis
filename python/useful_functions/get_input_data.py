import csv
from datetime import datetime
from datetime import timedelta
from pathlib import Path

input_data_path = str(Path(__file__).parents[1].joinpath("input_data"))


def get_spacecraft(filename):
    """
    Import orbit data from a CSV file.
    """
    with open(
        input_data_path + "/spacecraft/" + filename + ".csv",
        mode="r",
        encoding="utf_8_sig",
    ) as inp:
        reader = csv.reader(inp)
        spacecraft = {rows[0]: float(rows[1]) for rows in reader}
    return spacecraft


def get_station(filename):
    """
    Import orbit data from a CSV file.
    """
    with open(
        input_data_path + "/groundstations/" + filename + ".csv",
        mode="r",
        encoding="utf_8_sig",
    ) as inp:
        reader = csv.reader(inp)
        station = {rows[0]: float(rows[1]) for rows in reader}
    return station


def get_orbit(filename):
    """
    Import orbit data from a CSV file.
    """
    with open(
        input_data_path + "/orbits/" + filename + ".csv", mode="r", encoding="utf_8_sig"
    ) as inp:
        reader = csv.reader(inp)
        orbit = {rows[0]: float(rows[1]) for rows in reader}
    return orbit


def get_dates(filename):
    """
    Import dates from a CSV file.
    """
    with open(
        input_data_path + "/dates/" + filename + ".csv", mode="r", encoding="utf_8_sig"
    ) as inp:
        reader = csv.reader(inp)
        dates = {}
        for row in reader:
            if row[0] == "step_size":
                info = timedelta(seconds=int(row[1]))
            elif row[0] == "propagation_days":
                info = timedelta(days=int(row[1]))
            else:
                info = datetime.strptime(row[1], "%Y-%m-%d-%H:%M:%S")
            dates[row[0]] = info
    return dates
