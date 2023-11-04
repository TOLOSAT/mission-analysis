from iridium_doppler_GPSlocation import (
    IRIDIUM_visibility,
    IRIDIUM_windows,
    IRIDIUM_sat_results,
    selected_iridium,
    selected_iridium_nospace,
)

from useful_functions import plot_functions as pf

fig, axes = pf.dark_figure()
axes[0].plot(
    IRIDIUM_sat_results["seconds"] / 86400, IRIDIUM_sat_results["doppler_shift"] / 1e3
)
axes[0].set_title(f"Doppler shift of {selected_iridium}")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Doppler shift [kHz]")
axes[0].set_xlim(0, IRIDIUM_sat_results["seconds"].max() / 86400)
pf.finish_dark_figure(
    fig, f"results/{selected_iridium_nospace}_doppler_shift.png", show=True
)

fig, axes = pf.light_figure()
axes[0].plot(
    IRIDIUM_sat_results["seconds"] / 86400, IRIDIUM_sat_results["doppler_shift"] / 1e3
)
axes[0].set_title(f"Doppler shift of {selected_iridium}")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Doppler shift [kHz]")
axes[0].set_xlim(0, IRIDIUM_sat_results["seconds"].max() / 86400)
pf.finish_light_figure(
    fig, f"results/{selected_iridium_nospace}_doppler_shift_light.png", show=True
)

fig, axes = pf.dark_figure()
axes[0].plot(
    IRIDIUM_sat_results["seconds"] / 86400, IRIDIUM_sat_results["doppler_rate"]
)
axes[0].set_title(f"Doppler rate of {selected_iridium}")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Doppler rate [Hz/s]")
axes[0].set_xlim(0, IRIDIUM_sat_results["seconds"].max() / 86400)
pf.finish_dark_figure(
    fig, f"results/{selected_iridium_nospace}_doppler_rate.png", show=True
)

fig, axes = pf.light_figure()
axes[0].plot(
    IRIDIUM_sat_results["seconds"] / 86400, IRIDIUM_sat_results["doppler_rate"]
)
axes[0].set_title(f"Doppler rate of {selected_iridium}")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Doppler rate [Hz/s]")
axes[0].set_xlim(0, IRIDIUM_sat_results["seconds"].max() / 86400)
pf.finish_light_figure(
    fig, f"results/{selected_iridium_nospace}_doppler_rate_light.png", show=True
)

fig, axes = pf.dark_figure()
axes[0].plot(
    IRIDIUM_visibility["seconds"] / 86400,
    IRIDIUM_visibility["sum_ok"],
    linestyle="none",
    marker=".",
)
axes[0].set_title("Visibility of IRIDIUM satellites satisfying all 4 conditions")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Number of satellites [-]")
axes[0].set_xlim(0, IRIDIUM_visibility["seconds"].max() / 86400)
pf.finish_dark_figure(
    fig, "results/IRIDIUM_visibility.png", show=True, force_y_int=True
)

fig, axes = pf.light_figure()
axes[0].plot(
    IRIDIUM_visibility["seconds"] / 86400,
    IRIDIUM_visibility["sum_ok"],
    linestyle="none",
    marker=".",
)
axes[0].set_title("Visibility of IRIDIUM satellites satisfying all 4 conditions")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Number of satellites [-]")
axes[0].set_xlim(0, IRIDIUM_visibility["seconds"].max() / 86400)
pf.finish_light_figure(
    fig, "results/IRIDIUM_visibility_light.png", show=True, force_y_int=True
)

fig, axes = pf.dark_figure()
axes[0].vlines(IRIDIUM_windows["seconds"] / 86400, 0, IRIDIUM_windows["duration"] / 60)
axes[0].set_title("Visibility windows of at least one IRIDIUM satellite")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Window duration [mins]")
axes[0].set_ylim(0, IRIDIUM_windows["duration"].max() / 60)
axes[0].set_xlim(0, IRIDIUM_windows["seconds"].max() / 86400)
pf.finish_dark_figure(fig, "results/IRIDIUM_windows.png", show=True)

fig, axes = pf.light_figure()
axes[0].vlines(IRIDIUM_windows["seconds"] / 86400, 0, IRIDIUM_windows["duration"] / 60)
axes[0].set_title("Visibility windows of at least one IRIDIUM satellite")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Window duration [mins]")
axes[0].set_ylim(0, IRIDIUM_windows["duration"].max() / 60)
axes[0].set_xlim(0, IRIDIUM_windows["seconds"].max() / 86400)
pf.finish_light_figure(fig, "results/IRIDIUM_windows_light.png", show=True)
