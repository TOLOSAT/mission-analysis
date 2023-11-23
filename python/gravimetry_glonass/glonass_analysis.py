from glonass_doppler import (
    glonass_visibility,
    glonass_windows,
    glonass_sat_results,
    selected_glonass,
    selected_glonass_nospace,
)

from useful_functions import plot_functions as pf

fig, axes = pf.dark_figure()
axes[0].plot(glonass_sat_results["seconds"] / 86400, glonass_sat_results["doppler_shift"] / 1e3)
axes[0].set_title(f"Doppler shift of {selected_glonass}")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Doppler shift [kHz]")
axes[0].set_xlim(0, glonass_sat_results["seconds"].max() / 86400)
pf.finish_dark_figure(
    fig, f"results/{selected_glonass_nospace}_doppler_shift.png", show=True
)

fig, axes = pf.light_figure()
axes[0].plot(glonass_sat_results["seconds"] / 86400, glonass_sat_results["doppler_shift"] / 1e3)
axes[0].set_title(f"Doppler shift of {selected_glonass}")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Doppler shift [kHz]")
axes[0].set_xlim(0, glonass_sat_results["seconds"].max() / 86400)
pf.finish_light_figure(
    fig, f"results/{selected_glonass_nospace}_doppler_shift_light.png", show=True
)

fig, axes = pf.dark_figure()
axes[0].plot(glonass_sat_results["seconds"] / 86400, glonass_sat_results["doppler_rate"])
axes[0].set_title(f"Doppler rate of {selected_glonass}")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Doppler rate [Hz/s]")
axes[0].set_xlim(0, glonass_sat_results["seconds"].max() / 86400)
pf.finish_dark_figure(
    fig, f"results/{selected_glonass_nospace}_doppler_rate.png", show=True
)

fig, axes = pf.light_figure()
axes[0].plot(glonass_sat_results["seconds"] / 86400, glonass_sat_results["doppler_rate"])
axes[0].set_title(f"Doppler rate of {selected_glonass}")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Doppler rate [Hz/s]")
axes[0].set_xlim(0, glonass_sat_results["seconds"].max() / 86400)
pf.finish_light_figure(
    fig, f"results/{selected_glonass_nospace}_doppler_rate_light.png", show=True
)

fig, axes = pf.dark_figure()
axes[0].plot(
    glonass_visibility["seconds"] / 86400,
    glonass_visibility["sum_ok"],
    linestyle="none",
    marker=".",
)
axes[0].set_title("Visibility of glonass satellites satisfying all 4 conditions")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Number of satellites [-]")
axes[0].set_xlim(0, glonass_visibility["seconds"].max() / 86400)
pf.finish_dark_figure(fig, "results/glonass_visibility.png", show=True, force_y_int=True)

fig, axes = pf.light_figure()
axes[0].plot(
    glonass_visibility["seconds"] / 86400,
    glonass_visibility["sum_ok"],
    linestyle="none",
    marker=".",
)
axes[0].set_title("Visibility of glonass satellites satisfying all 4 conditions")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Number of satellites [-]")
axes[0].set_xlim(0, glonass_visibility["seconds"].max() / 86400)
pf.finish_light_figure(
    fig, "results/glonass_visibility_light.png", show=True, force_y_int=True
)

fig, axes = pf.dark_figure()
axes[0].vlines(glonass_windows["seconds"] / 86400, 0, glonass_windows["duration"] / 60)
axes[0].set_title("Visibility windows of at least one glonass satellite")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Window duration [mins]")
axes[0].set_ylim(0, glonass_windows["duration"].max() / 60)
axes[0].set_xlim(0, glonass_windows["seconds"].max() / 86400)
pf.finish_dark_figure(fig, "results/glonass_windows.png", show=True)

fig, axes = pf.light_figure()
axes[0].vlines(glonass_windows["seconds"] / 86400, 0, glonass_windows["duration"] / 60)
axes[0].set_title("Visibility windows of at least one glonass satellite")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Window duration [mins]")
axes[0].set_ylim(0, glonass_windows["duration"].max() / 60)
axes[0].set_xlim(0, glonass_windows["seconds"].max() / 86400)
pf.finish_light_figure(fig, "results/glonass_windows_light.png", show=True)
