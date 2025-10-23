import os
import pandas as pd
import numpy as np
from useful_functions import plot_functions as pf

# =============================
# Configuration
# =============================
selected_iridium = "IRIDIUM 100"
selected_iridium_nospace = selected_iridium.replace(" ", "_")
results_dir = "results/1orbit"

# Choose time unit: "seconds", "hours", or "days"
time_unit = "minutes"  # Change this depending on your simulation
unit_factors = {
    "seconds": 1,
    "minutes": 60,
    "hours": 3600,
    "days": 86400,
    "years": 365.25,
}
time_factor = unit_factors[time_unit]
time_label = f"Time since launch [{time_unit}]"

# =============================
# Load data
# =============================
iridium_visibility = pd.read_csv(os.path.join(results_dir, "iridium_visibility.csv"), low_memory=False)
iridium_windows = pd.read_csv(os.path.join(results_dir, "iridium_windows.csv"), low_memory=False)
iridium_sat_results = pd.read_csv(os.path.join(results_dir, "iridium_sat_results.csv"), low_memory=False)

# =============================
# Plot 1: Doppler Shift
# =============================
for style in ["dark", "light"]:
    fig, axes = getattr(pf, f"{style}_figure")()
    axes[0].plot(iridium_sat_results["seconds"] / time_factor, iridium_sat_results["doppler_shift"] / 1e3)
    axes[0].set_title(f"Doppler shift of {selected_iridium}")
    axes[0].set_xlabel(time_label)
    axes[0].set_ylabel("Doppler shift [kHz]")
    axes[0].set_xlim(0, iridium_sat_results["seconds"].max() / time_factor)
    getattr(pf, f"finish_{style}_figure")(
        fig, os.path.join(results_dir, f"{selected_iridium_nospace}_doppler_shift_{style}.png"), show=True
    )

# =============================
# Plot 2: Doppler Rate
# =============================
for style in ["dark", "light"]:
    fig, axes = getattr(pf, f"{style}_figure")()
    axes[0].plot(iridium_sat_results["seconds"] / time_factor, iridium_sat_results["doppler_rate"])
    axes[0].set_title(f"Doppler rate of {selected_iridium}")
    axes[0].set_xlabel(time_label)
    axes[0].set_ylabel("Doppler rate [Hz/s]")
    axes[0].set_xlim(0, iridium_sat_results["seconds"].max() / time_factor)
    getattr(pf, f"finish_{style}_figure")(
        fig, os.path.join(results_dir, f"{selected_iridium_nospace}_doppler_rate_{style}.png"), show=True
    )

# =============================
# Plot 3: Visibility Count
# =============================
for style in ["dark", "light"]:
    fig, axes = getattr(pf, f"{style}_figure")()
    axes[0].plot(iridium_visibility["seconds"] / time_factor, iridium_visibility["sum_ok"], linestyle="none", marker=".")
    axes[0].set_title("Visibility of iridium satellites satisfying all 4 conditions")
    axes[0].set_xlabel(time_label)
    axes[0].set_ylabel("Number of satellites [-]")
    axes[0].set_xlim(0, iridium_visibility["seconds"].max() / time_factor)
    getattr(pf, f"finish_{style}_figure")(
        fig, os.path.join(results_dir, f"iridium_visibility_{style}.png"), show=True, force_y_int=True
    )

# =============================
# Plot 4: Visibility Windows
# =============================
for style in ["dark", "light"]:
    fig, axes = getattr(pf, f"{style}_figure")()
    x_vals = iridium_windows["seconds"] / time_factor
    y_vals = iridium_windows["duration"] / 60
    if not x_vals.empty and not y_vals.empty:
        axes[0].vlines(x_vals, 0, y_vals, linewidth=2)
        axes[0].set_ylim(0, max(y_vals.max() * 1.1, 1))
        axes[0].set_xlim(-0.01, x_vals.max() + 0.01)
    else:
        axes[0].text(0.5, 0.5, "No visibility windows", transform=axes[0].transAxes, ha="center", va="center")
    axes[0].set_title("Visibility windows of at least one iridium satellite")
    axes[0].set_xlabel(time_label)
    axes[0].set_ylabel("Window duration [mins]")
    axes[0].set_xlim(0, x_vals.max() if not x_vals.empty else 1)
    getattr(pf, f"finish_{style}_figure")(
        fig, os.path.join(results_dir, f"iridium_windows_{style}.png"), show=True
    )

import matplotlib.patches as mpatches

# =============================
# Plot 5: Histogram of Window Durations
# =============================
durations_min = iridium_windows["duration"] / 60  # seconds to minutes

mean_dur = durations_min.mean()
median_dur = durations_min.median()

# Text box content
param_text = f"Mean: {mean_dur:.1f} min\nMedian: {median_dur:.1f} min"
textbox_x = 0.7  # Position in figure coordinates (0–1)
textbox_y = 0.85

for style in ["dark", "light"]:
    fig, axes = getattr(pf, f"{style}_figure")()

    # Plot histogram
    axes[0].hist(durations_min, bins=30, color="skyblue", edgecolor="black")
    axes[0].set_xlabel("Window duration [min]")
    axes[0].set_ylabel("Count")
    axes[0].set_title("Visibility duration of Iridium windows")
    axes[0].grid(True)

    # Place annotation box
    fig.text(
        textbox_x, textbox_y,
        param_text,
        fontsize=10,
        verticalalignment='top',
        bbox=dict(boxstyle="round", facecolor='white', edgecolor='lightgray', alpha=0.9)
    )

    getattr(pf, f"finish_{style}_figure")(
        fig,
        os.path.join(results_dir, f"iridium_visibility_duration_stats_{style}.png"),
        show=True
    )


# =============================
# Visibility coverage calculation
# =============================
# Compute total simulation duration in seconds
total_time_seconds = iridium_visibility["seconds"].max()
total_time_days = total_time_seconds / 86400

# Get all merged visibility intervals (seconds since start)
merged_segments = iridium_windows[["start", "end"]].copy()
start_time = pd.to_datetime(iridium_windows["start"].iloc[0])
merged_segments["start_s"] = (pd.to_datetime(merged_segments["start"]) - start_time).dt.total_seconds()
merged_segments["end_s"] = (pd.to_datetime(merged_segments["end"]) - start_time).dt.total_seconds()
merged_segments = merged_segments[["start_s", "end_s"]].sort_values("start_s").values.tolist()

# Merge overlapping/adjacent intervals
merged_intervals = []
for start, end in merged_segments:
    if not merged_intervals:
        merged_intervals.append([start, end])
    else:
        last_start, last_end = merged_intervals[-1]
        if start <= last_end:
            merged_intervals[-1][1] = max(last_end, end)
        else:
            merged_intervals.append([start, end])

# Calculate total visibility
total_unique_visibility_seconds = sum((end - start) for start, end in merged_intervals)
total_unique_visibility_days = total_unique_visibility_seconds / 86400
coverage_percentage = 100 * total_unique_visibility_days / total_time_days

# Durations of individual windows
all_durations = iridium_windows["duration"].to_numpy()

# =============================
# Save stats
# =============================
with open(os.path.join(results_dir, "iridium_visibility_stats.txt"), "w") as f:
    f.write("=== iridium Visibility Stats ===\n")
    f.write(f"Total simulation duration: {total_time_days:.3f} days\n")
    f.write(f"Total time with visibility of at least one iridium satellite (satisfying the 4 conditions): {total_unique_visibility_days:.3f} days\n")
    f.write(f"Overall visibility coverage (% of simulation time with at least one visible satellite): {coverage_percentage:.2f} %\n")
    f.write(f"Number of individual visibility intervals: {len(all_durations)}\n")
    f.write(f"Average duration of visibility intervals: {np.mean(all_durations):.1f} seconds\n")
    f.write(f"Maximum duration of a visibility interval: {np.max(all_durations):.1f} seconds\n")
    f.write(f"Minimum duration of a visibility interval: {np.min(all_durations):.1f} seconds\n")
