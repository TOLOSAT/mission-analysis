import os
from datetime import datetime, timezone
from math import prod
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
from matplotlib.ticker import MaxNLocator

assets_path = str(Path(__file__).parents[2].joinpath("assets"))


# Function to prepare output folder and return path
def get_plot_path(target_folder):
    path = os.path.dirname(os.path.realpath(__file__)).replace(
        "PythonPlots", target_folder
    )
    os.makedirs(
        os.path.dirname(os.path.realpath(__file__)) + "/" + target_folder, exist_ok=True
    )
    return path


# Functions for figures
def dark_figure(subplots=(1, 1), figsize=(7, 5.2)):
    fig = plt.figure(facecolor="#0D1117", figsize=figsize)
    axes = []
    for ii in range(0, prod(subplots)):
        axes.append(
            fig.add_subplot(subplots[0], subplots[1], ii + 1, facecolor="#0D1117")
        )
        axes[ii].tick_params(axis="x", colors="white", which="both")
        axes[ii].tick_params(axis="y", colors="white", which="both")
        axes[ii].yaxis.label.set_color("white")
        axes[ii].xaxis.label.set_color("white")
        axes[ii].title.set_color("white")
        axes[ii].grid(color="#161C22", linewidth=0.5)
        for i in axes[ii].spines:
            axes[ii].spines[i].set_color("white")
    return fig, axes


def light_figure(subplots=(1, 1), figsize=(7, 5.2)):
    fig = plt.figure(facecolor="white", figsize=figsize)
    axes = []
    for ii in range(0, prod(subplots)):
        axes.append(
            fig.add_subplot(subplots[0], subplots[1], ii + 1, facecolor="white")
        )
        axes[ii].tick_params(axis="x", colors="black", which="both")
        axes[ii].tick_params(axis="y", colors="black", which="both")
        axes[ii].yaxis.label.set_color("black")
        axes[ii].xaxis.label.set_color("black")
        axes[ii].title.set_color("black")
        axes[ii].grid(color="lightgrey", linewidth=0.5)
        for i in axes[ii].spines:
            axes[ii].spines[i].set_color("black")
    return fig, axes


def finish_dark_figure(fig, path, show=True, force_x_int=False, force_y_int=False):
    plt.tight_layout()
    if force_x_int:
        for ax in fig.axes:
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    if force_y_int:
        for ax in fig.axes:
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    fig.subplots_adjust(bottom=0.20)
    fig_axes1 = fig.add_axes([0.772, 0.01, 0.22, 0.3], anchor="SE", zorder=1)
    Badge_TOLOSAT_dark = Image.open(assets_path + "/TOLOSAT_dark.png")
    fig_axes1.imshow(Badge_TOLOSAT_dark)
    Badge_TOLOSAT_dark.close()
    fig_axes1.axis("off")
    fig_axes2 = fig.add_axes([0.02, 0.02, 1, 1], anchor="SW", zorder=1)
    fig_axes2.text(
        0,
        0,
        datetime.now(timezone.utc).strftime(
            "Plot generated on %Y/%m/%d at %H:%M:%S UTC."
        ),
        color="dimgray",
    )
    fig_axes2.axis("off")
    plt.savefig(path, transparent=False, dpi=500)
    if show:
        plt.show()
    plt.close()


def finish_light_figure(fig, path, show=True, force_x_int=False, force_y_int=False):
    plt.tight_layout()
    if force_x_int:
        for ax in fig.axes:
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    if force_y_int:
        for ax in fig.axes:
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    fig.subplots_adjust(bottom=0.20)
    fig_axes1 = fig.add_axes([0.772, 0.01, 0.22, 0.3], anchor="SE", zorder=1)
    Badge_TOLOSAT_light = Image.open(assets_path + "/TOLOSAT_light.png")
    fig_axes1.imshow(Badge_TOLOSAT_light)
    Badge_TOLOSAT_light.close()
    fig_axes1.axis("off")
    fig_axes2 = fig.add_axes([0.02, 0.02, 1, 1], anchor="SW", zorder=1)
    fig_axes2.text(
        0,
        0,
        datetime.now(timezone.utc).strftime(
            "Plot generated on %Y/%m/%d at %H:%M:%S UTC."
        ),
        color="silver",
    )
    fig_axes2.axis("off")
    plt.savefig(path, transparent=False, dpi=500)
    if show:
        plt.show()
    plt.close()


def flip_legend(ncol, reverse=False, handles_in=None, labels_in=None):
    if handles_in is None and labels_in is None:
        handles_, labels_ = plt.gca().get_legend_handles_labels()
    else:
        handles_ = handles_in
        labels_ = labels_in
    handles_ = [k for j in [handles_[i::ncol] for i in range(ncol)] for k in j]
    labels_ = [k for j in [labels_[i::ncol] for i in range(ncol)] for k in j]
    if reverse:
        return handles_[::-1], labels_[::-1]
    else:
        return handles_, labels_


def flatten(list_of_lists):
    flattened_list = []
    for i in list_of_lists:
        if isinstance(i, list):
            flattened_list += i
        else:
            flattened_list.append(i)
    return flattened_list


def plot_sphere(ax, center, radius):
    u, v = np.mgrid[0: 2 * np.pi: 50j, 0: np.pi: 50j]
    x = radius * np.cos(u) * np.sin(v)
    y = radius * np.sin(u) * np.sin(v)
    z = radius * np.cos(v)
    ax.plot_surface(
        x - center[0], y - center[1], z - center[2], color="cyan", alpha=0.5
    )


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
    fig = go.Figure(
        data=go.Scatter3d(x=sat_x, y=sat_y, z=sat_z, marker=dict(size=2, color=time))
    )
    [earth_x, earth_y, earth_z] = plotly_sphere([0, 0, 0], 6371008.366666666)
    fig.add_mesh3d(
        x=earth_x / 1e3,
        y=earth_y / 1e3,
        z=earth_z / 1e3,
        alphahull=0,
        color="darkblue",
        opacity=0.5,
        hoverinfo="skip",
    )
    fig.update_layout(
        template="plotly_dark",
        scene=dict(xaxis_title="x [km]", yaxis_title="y [km]", zaxis_title="z [km]"),
    )
    return fig


def remove_html_margins(path):
    with open(path, "r") as f:
        lines = f.readlines()
    with open(path, "w") as f:
        for line in lines:
            if "<head>" in line:
                f.write(
                    line.replace("<head>", "<head><style>body { margin: 0; }</style>")
                )
            else:
                f.write(line)


def finish_plotly_figure(fig, path):
    fig.write_html(path)
    remove_html_margins(path)


def plotly_groundtrack(time, lon, lat):
    df = pd.DataFrame({"lon": lon, "lat": lat, "time": time})
    df["time"] = pd.to_timedelta(df["time"], unit="seconds")

    frames = []
    for time in df["time"]:
        frames.append(
            go.Frame(
                name=str(pd.to_timedelta(time, unit="seconds")),
                data=[
                    go.Scattergeo(
                        lon=df[
                            (df["time"] <= time)
                            & (df["time"] >= time - pd.to_timedelta(90, unit="minutes"))
                            ]["lon"],
                        lat=df[
                            (df["time"] <= time)
                            & (df["time"] >= time - pd.to_timedelta(90, unit="minutes"))
                            ]["lat"],
                        mode="lines",
                        line=dict(width=2, color="blue"),
                    ),
                    go.Scattergeo(
                        lon=df[df["time"] == time]["lon"],
                        lat=df[df["time"] == time]["lat"],
                        mode="markers",
                        marker=dict(size=5, color="orange"),
                        text="Tolosat",
                    ),
                ],
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

    fig.update_traces(hovertemplate=None, hoverinfo="skip")
    fig.update_layout(template="plotly_dark")
    return fig
