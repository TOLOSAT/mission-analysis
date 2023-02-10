from results_processing import results_dict
from useful_functions import *
import plotly.graph_objects as go

data = []
for sat in results_dict:
    if sat == "epochs":
        continue
    data.append(
        go.Scatter3d(
            name=sat,
            x=results_dict[sat]["x"][0:1000] / 1e3,
            y=results_dict[sat]["y"][0:1000] / 1e3,
            z=results_dict[sat]["z"][0:1000] / 1e3,
            mode="markers",
            marker=dict(size=2, color=results_dict["epochs"][0:1000]),
        )
    )
fig = go.Figure(data=data)
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
finish_plotly_figure(fig, f"iridium_visualization.html")

seconds_elapsed = results_dict["epochs"] - results_dict["epochs"][0]
frames = []
[earth_x, earth_y, earth_z] = plotly_sphere([0, 0, 0], 6371008.366666666)
for time in range(180):
    data = [
        go.Mesh3d(
            x=earth_x / 1e3,
            y=earth_y / 1e3,
            z=earth_z / 1e3,
            alphahull=0,
            color="darkblue",
            opacity=0.5,
            hoverinfo="skip",
        )
    ]
    for sat in results_dict:
        if sat == "epochs":
            continue
        data.append(
            go.Scatter3d(
                name=sat,
                x=results_dict[sat][seconds_elapsed == (time * 60)]["x"] / 1e3,
                y=results_dict[sat][seconds_elapsed == (time * 60)]["y"] / 1e3,
                z=results_dict[sat][seconds_elapsed == (time * 60)]["z"] / 1e3,
                mode="markers",
                marker=dict(size=2),
            )
        )

    frames.append(
        go.Frame(
            name=str(pd.to_timedelta(time, unit="minutes")).replace("0 days ", ""),
            data=data,
            layout=go.Layout(
                scene=dict(
                    xaxis=dict(range=[-8000, 8000]),
                    yaxis=dict(range=[-8000, 8000]),
                    zaxis=dict(range=[-8000, 8000]),
                )
            ),
        )
    )
# now create figure and add play button and slider
fig = go.Figure(
    data=frames[0].data,
    frames=frames,
    layout={
        "updatemenus": [
            {
                "type": "buttons",
                "buttons": [
                    {
                        "args": [
                            None,
                            {
                                "frame": {"duration": 500, "redraw": False},
                                "fromcurrent": True,
                                "transition": {
                                    "duration": 300,
                                    "easing": "quadratic-in-out",
                                },
                            },
                        ],
                        "label": "Play",
                        "method": "animate",
                    },
                    {
                        "args": [
                            [None],
                            {
                                "frame": {"duration": 0, "redraw": False},
                                "mode": "immediate",
                                "transition": {"duration": 0},
                            },
                        ],
                        "label": "Pause",
                        "method": "animate",
                    },
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top",
            }
        ],
        "sliders": [
            {
                "active": 0,
                "yanchor": "top",
                "xanchor": "left",
                "currentvalue": {
                    "font": {"size": 20},
                    "visible": True,
                    "xanchor": "right",
                },
                "transition": {"duration": 300, "easing": "cubic-in-out"},
                "pad": {"b": 10, "t": 50},
                "len": 0.9,
                "x": 0.1,
                "y": 0,
                "steps": [
                    {
                        "label": f.name,
                        "method": "animate",
                        "args": [
                            [f.name],
                            {
                                "frame": {"duration": 300, "redraw": False},
                                "mode": "immediate",
                                "transition": {"duration": 300},
                            },
                        ],
                    }
                    for f in frames
                ],
            }
        ],
    },
)
fig.update_traces(hovertemplate=None, hoverinfo="skip")
fig.update_layout(template="plotly_dark")
finish_plotly_figure(fig, f"iridium_animation.html")
