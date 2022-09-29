import csv
from datetime import datetime, timedelta
from os import makedirs
from pathlib import Path
import pandas as pd

import numpy as np
import plotly.graph_objects as go
from pyproj import Transformer

input_data_path = str(Path(__file__).parents[0].joinpath('input_data'))

output_columns = ["time", "eci_x", "eci_y", "eci_z", "eci_vx", "eci_vy", "eci_vz", "kep_sma", "kep_ecc", "kep_inc",
                  "kep_aop", "kep_raan", "kep_ta", "ecef_x", "ecef_y", "ecef_z", "ecef_vx", "ecef_vy", "ecef_vz"]


def plot_sphere(ax, center, radius):
    u, v = np.mgrid[0:2 * np.pi:50j, 0:np.pi:50j]
    x = radius * np.cos(u) * np.sin(v)
    y = radius * np.sin(u) * np.sin(v)
    z = radius * np.cos(v)
    ax.plot_surface(x - center[0], y - center[1], z - center[2], color='cyan', alpha=0.5)


def plotly_sphere(center, radius):
    nb_points = 50
    x = np.zeros(nb_points ** 2) * np.NaN
    y = np.zeros(nb_points ** 2) * np.NaN
    z = np.zeros(nb_points ** 2) * np.NaN
    ii = 0
    for theta in np.linspace(0, 2 * np.pi, nb_points):
        for phi in np.linspace(0, np.pi, nb_points):
            x[ii] = radius * np.cos(theta) * np.sin(phi)
            y[ii] = radius * np.sin(theta) * np.sin(phi)
            z[ii] = radius * np.cos(phi)
            ii += 1
    return x - center[0], y - center[1], z - center[2]


def plotly_trajectory(time, sat_x, sat_y, sat_z):
    fig = go.Figure(data=go.Scatter3d(
        x=sat_x, y=sat_y, z=sat_z,
        marker=dict(
            size=2,
            color=time
        )
    ))
    [earth_x, earth_y, earth_z] = plotly_sphere([0, 0, 0], 6371008.366666666)
    fig.add_mesh3d(
        x=earth_x / 1E3, y=earth_y / 1E3, z=earth_z / 1E3,
        alphahull=0,
        color='darkblue',
        opacity=0.5,
        hoverinfo='skip'
    )
    fig.update_layout(template='plotly_dark',
                      scene=dict(
                          xaxis_title='x [km]',
                          yaxis_title='y [km]',
                          zaxis_title='z [km]'))
    return fig


def get_spacecraft(filename):
    """
    Import orbit data from a CSV file.
    """
    with open(input_data_path + '/spacecraft/' + filename + '.csv', mode='r', encoding='utf_8_sig') as inp:
        reader = csv.reader(inp)
        spacecraft = {rows[0]: float(rows[1]) for rows in reader}
    return spacecraft


def get_station(filename):
    """
    Import orbit data from a CSV file.
    """
    with open(input_data_path + '/groundstations/' + filename + '.csv', mode='r', encoding='utf_8_sig') as inp:
        reader = csv.reader(inp)
        station = {rows[0]: float(rows[1]) for rows in reader}
    return station


def get_orbit(filename):
    """
    Import orbit data from a CSV file.
    """
    with open(input_data_path + '/orbits/' + filename + '.csv', mode='r', encoding='utf_8_sig') as inp:
        reader = csv.reader(inp)
        orbit = {rows[0]: float(rows[1]) for rows in reader}
    return orbit


def get_dates(filename):
    """
    Import dates from a CSV file.
    """
    with open(input_data_path + '/dates/' + filename + '.csv', mode='r', encoding='utf_8_sig') as inp:
        reader = csv.reader(inp)
        dates = {}
        for row in reader:
            if row[0] == 'step_size':
                info = timedelta(seconds=int(row[1]))
            else:
                info = datetime.strptime(row[1], '%Y-%m-%d-%H:%M:%S')
            dates[row[0]] = info
    return dates


def compute_visibility(pos_ecf, station):
    """
    Compute the visibility of the spacecraft from a given ground station.
    """
    transformer = Transformer.from_crs(
        {"proj": 'latlong', "ellps": 'WGS84', "datum": 'WGS84'},
        {"proj": 'geocent', "ellps": 'WGS84', "datum": 'WGS84'},
    )
    station_ecf = transformer.transform(station["longitude"], station["latitude"], station["altitude"], radians=False)
    station_sat_vector = pos_ecf - station_ecf
    station_ecf_unit = station_ecf / np.linalg.norm(station_ecf)
    station_sat_vector_unit = station_sat_vector.T / np.apply_along_axis(np.linalg.norm, 1, station_sat_vector)
    dot_product = np.dot(station_ecf_unit, station_sat_vector_unit)
    elevation = 90 - np.arccos(dot_product) * 180 / np.pi
    visibility = elevation >= station["minimum_elevation"]
    return visibility, elevation


def ecf2lla(pos_ecf):
    """
    Convert ECF coordinates to LLA coordinates.
    """
    transformer = Transformer.from_crs(
        {"proj": 'geocent', "ellps": 'WGS84', "datum": 'WGS84'},
        {"proj": 'latlong', "ellps": 'WGS84', "datum": 'WGS84'}
    )
    out_lla = transformer.transform(pos_ecf[:, 0], pos_ecf[:, 1], pos_ecf[:, 2], radians=False)
    return np.array(out_lla).T


def write_results(spacecraft_name, orbit_name, dates_name, array):
    """
    Export propagation results to a CSV file.
    """
    makedirs('results/', exist_ok=True)
    for ii in enumerate(output_columns):
        np.savetxt(f'results/{spacecraft_name}_{orbit_name}_{dates_name}_{ii[1]}.csv', array, delimiter=",")


def remove_html_margins(path):
    with open(path, 'r') as f:
        lines = f.readlines()
    with open(path, 'w') as f:
        for line in lines:
            if '<head>' in line:
                f.write(line.replace('<head>', '<head><style>body { margin: 0; }</style>'))
            else:
                f.write(line)


def finish_plotly_figure(fig, path):
    fig.write_html(path)
    remove_html_margins(path)


def plotly_groundtrack(time, lon, lat):
    df = pd.DataFrame({'lon': lon, 'lat': lat, 'time': time})
    df['time'] = pd.to_timedelta(df['time'], unit="seconds")

    frames = []
    for time in df['time']:
        frames.append(
            go.Frame(
                name=str(pd.to_timedelta(time, unit="seconds")),
                data=[go.Scattergeo(
                    lon=df[(df['time'] <= time) & (df['time'] >= time - pd.to_timedelta(90, unit="minutes"))]['lon'],
                    lat=df[(df['time'] <= time) & (df['time'] >= time - pd.to_timedelta(90, unit="minutes"))]['lat'],
                    mode="lines",
                    line=dict(width=2, color="blue"),
                ),
                    go.Scattergeo(
                        lon=df[df['time'] == time]['lon'],
                        lat=df[df['time'] == time]['lat'],
                        mode="markers",
                        marker=dict(size=5, color="orange"),
                        text="Tolosat"
                    )
                ]

            )
        )

    # now create figure and add play button and slider
    fig = go.Figure(
        data=frames[0].data,
        frames=frames,
        layout={
            # "updatemenus": [
            #     {
            #         "type": "buttons",
            #         "buttons": [{"label": "Play", "method": "animate", "args": [None]}],
            #     }
            # ],
            "sliders": [
                {
                    "active": 0,
                    "steps": [
                        {
                            "label": f.name,
                            "method": "animate",
                            "args": [[f.name]],
                        }
                        for f in frames
                    ],
                }
            ],
        },
    ).update_geos(
        scope="world",
    )

    fig.update_traces(hovertemplate=None, hoverinfo='skip')
    fig.update_layout(template='plotly_dark')
    return fig
