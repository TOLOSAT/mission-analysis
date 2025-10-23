import numpy as np
import os
from useful_functions import plot_functions as pf
import matplotlib.pyplot as plt

results_dir = os.path.join(os.path.dirname(__file__), "results/3years")

# Upload propagation results
states_array = np.load("results/3years/state_history.npy")
dep_vars_array = np.load("results/3years/dependent_variables.npy")

# Time in days
time_days = dep_vars_array[:, 0] / 86400 - dep_vars_array[1, 0] / 86400
time_hours = dep_vars_array[:,0]/3600 - dep_vars_array[1,0]/3600
time_seconds = dep_vars_array[:, 0] - dep_vars_array[1,0]


# ----------------------------
# Total acceleration norm
# ----------------------------
acc_total = np.linalg.norm(dep_vars_array[:, 1:4], axis=1)

for style in ["dark", "light"]:
    fig, axes = getattr(pf, f"{style}_figure")()
    axes[0].plot(time_days, acc_total)
    axes[0].set_title("Total acceleration norm on TOLOSAT")
    axes[0].set_xlabel("Time since launch [days]")
    axes[0].set_ylabel("Acceleration [m/s$^2$]")
    getattr(pf, f"finish_{style}_figure")(
        fig, os.path.join(results_dir, f"tolosat_total_acceleration_{style}.png"), show=True
    )


# ----------------------------
# Individual accelerations (Earth gravity, Drag, SRP, Moon, Sun)
# ----------------------------
acc_gravity_earth = dep_vars_array[:, 12]
acc_drag = dep_vars_array[:, 13]
acc_srp = dep_vars_array[:, 14]
acc_sun = dep_vars_array[:, 15]
acc_moon = dep_vars_array[:, 16]

for style in ["dark", "light"]:
    fig, axes = getattr(pf, f"{style}_figure")()
    axes[0].plot(time_days, acc_gravity_earth, label="Earth Gravity")
    axes[0].plot(time_days, acc_drag, label="Drag")
    axes[0].plot(time_days, acc_srp, label="SRP")
    axes[0].plot(time_days, acc_moon, label="Moon Gravity")
    axes[0].plot(time_days, acc_sun, label="Sun Gravity")

    axes[0].set_yscale("log")
    axes[0].set_title("Individual acceleration norms on TOLOSAT")
    axes[0].set_xlabel("Time since launch [days]")
    axes[0].set_ylabel("Acceleration [m/s²]")
    axes[0].legend(bbox_to_anchor=(1.01, 0.5), loc="center left")
    axes[0].grid(True, which="both", linestyle="--", alpha=0.5)

    getattr(pf, f"finish_{style}_figure")(
        fig,
        os.path.join(results_dir, f"tolosat_individual_accelerations_{style}.png"),
        show=True,
    )

## ----------------------------
# Keplerian elements (3×2)
# ----------------------------
kepler_elements = dep_vars_array[:, 4:10]
labels = ["Semi-major axis [km]", "Eccentricity", "Inclination [deg]", "Argument of Perigee [deg]", "RAAN [deg]", "True Anomaly [deg]"]
units = [1e-3, 1, np.rad2deg, np.rad2deg, np.rad2deg, np.rad2deg]

for style in ["dark", "light"]:
    filename = f"tolosat_kepler_elements_{style}.png"
    path = os.path.join(results_dir, filename)

    fig, axes = getattr(pf, f"{style}_figure_subplots")(
        rows=3,
        cols=2,
        figsize=(14, 12),
        suptitle="Keplerian elements over time",
    )

    for i in range(min(6, len(axes))):
        y = kepler_elements[:, i]
        y = units[i](y) if callable(units[i]) else y * units[i]
        axes[i].plot(time_days, y)
        axes[i].set_ylabel(labels[i])
        axes[i].set_xlabel("Time [days]")

    plt.savefig(path, dpi=500)
    plt.show()
    plt.close()


# ----------------------------
# Altitude vs time
# ----------------------------
earth_radius_m = 6378137.0  # WGS84
position_vectors = states_array[:, 1:4]  # x, y, z
altitude_km = (np.linalg.norm(position_vectors, axis=1) - earth_radius_m) / 1e3

for style in ["dark", "light"]:
    fig, axes = getattr(pf, f"{style}_figure")()
    axes[0].plot(time_days, altitude_km)
    axes[0].set_title("Altitude over time")
    axes[0].set_xlabel("Time since launch [days]")
    axes[0].set_ylabel("Altitude [km]")
    getattr(pf, f"finish_{style}_figure")(
        fig, os.path.join(results_dir, f"tolosat_altitude_{style}.png"), show=True
    )

# ----------------------------
# Ground Track
# ----------------------------
lat = np.rad2deg(dep_vars_array[:, 10])
lon = np.rad2deg(dep_vars_array[:, 11])

for style in ["dark", "light"]:
    fig, axes = getattr(pf, f"{style}_figure")()
    axes[0].scatter(lon, lat, s=0.5)
    axes[0].scatter(lon[0], lat[0], label="Start", color="green", marker="o")
    axes[0].scatter(lon[-1], lat[-1], label="End", color="red", marker="x")
    axes[0].set_title("TOLOSAT Ground Track (full duration)")
    axes[0].set_xlabel("Longitude [deg]")
    axes[0].set_ylabel("Latitude [deg]")
    axes[0].set_xlim(-180, 180)
    axes[0].set_ylim(-90, 90)
    getattr(pf, f"finish_{style}_figure")(
        fig, os.path.join(results_dir, f"tolosat_ground_track_{style}.png"), show=True
    )

# ----------------------------
# Ground track with background map image
# ----------------------------

background_image_path = os.path.join(os.path.dirname(__file__), "earth_map.png")

for style in ["dark", "light"]:
    fig, axes = getattr(pf, f"{style}_figure")(figsize=(12, 6))
    ax = axes[0]

    # Load and show background image
    img = plt.imread(background_image_path)
    ax.imshow(img, extent=[-180, 180, -90, 90], aspect="auto", zorder=0)

    # Ground track
    ax.scatter(lon, lat, color="red", s=1, label="Ground track", zorder=1)
    ax.scatter(lon[0], lat[0], color="green", s=30, label="Start", zorder=2)
    ax.scatter(lon[-1], lat[-1], color="yellow", s=30, label="End", zorder=2)

    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")
    ax.set_title("TOLOSAT Ground Track on Earth Map")

    ax.grid(False)
    ax.legend(bbox_to_anchor=(1.01, 0.5), loc="center left")

    getattr(pf, f"finish_{style}_figure")(
        fig,
        os.path.join(results_dir, f"tolosat_ground_track_map_{style}.png"),
        show=True,
    )

# ----------------------------
# Orbital Energy Plots
# ----------------------------
mu_earth = 3.986004418e14  # [m^3/s^2] Earth's gravitational parameter

# Extract position and velocity vectors
positions = states_array[:, 1:4]  # x, y, z in m
velocities = states_array[:, 4:7]  # vx, vy, vz in m/s

r = np.linalg.norm(positions, axis=1)
v = np.linalg.norm(velocities, axis=1)

kinetic_energy = 0.5 * v**2
potential_energy = -mu_earth / r
total_energy = kinetic_energy + potential_energy
delta_energy = total_energy - total_energy[0]

for style in ["dark", "light"]:
    fig, axes = getattr(pf, f"{style}_figure")()

    axes[0].plot(time_days, kinetic_energy, label="Kinetic Energy", color="blue")
    axes[0].plot(time_days, potential_energy, label="Potential Energy", color="orange")
    axes[0].plot(time_days, total_energy, label="Total Energy", color="green")
    axes[0].plot(time_days, delta_energy, label="Δ Total Energy", color="red", linestyle="--")

    axes[0].set_xlabel("Time since launch [days]")
    axes[0].set_ylabel("Specific Energy [J/kg]")
    axes[0].set_title("Orbital Energy Components Over Time")
    axes[0].legend(bbox_to_anchor=(1.01, 0.5), loc="center left")
    axes[0].grid(True, which="both", linestyle="--", alpha=0.6)

    getattr(pf, f"finish_{style}_figure")(
        fig, os.path.join(results_dir, f"tolosat_energies_{style}.png"), show=True
    )
