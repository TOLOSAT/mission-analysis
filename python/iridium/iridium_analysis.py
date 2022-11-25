from datetime import timedelta

from iridium_doppler import results
from useful_functions import plot_functions as pf

fig, axes = pf.dark_figure()
axes[0].plot(results["timedelta"].dt.total_seconds() / 86400, results['IRIDIUM 73']["doppler_shift"])
axes[0].set_title("Doppler shift of IRIDIUM 73")
axes[0].set_xlabel("Time [days]")
axes[0].set_ylabel("Doppler shift [Hz]")
axes[0].set_xlim(0, max(results["timedelta"].dt.total_seconds()) / 86400)
pf.finish_dark_figure(fig, "IRIDIUM_73_doppler_shift.png", show=True)

fig, axes = pf.dark_figure()
axes[0].plot(results["timedelta"].dt.total_seconds() / 86400, results['IRIDIUM 73']["doppler_rate"])
axes[0].set_title("Doppler rate of IRIDIUM 73")
axes[0].set_xlabel("Time [days]")
axes[0].set_ylabel("Doppler rate [Hz/s]")
axes[0].set_xlim(0, max(results["timedelta"].dt.total_seconds()) / 86400)
pf.finish_dark_figure(fig, "IRIDIUM_73_doppler_rate.png", show=True)

IRIDIUM_visible = None
for sat in results:
    if "IRIDIUM" not in sat:
        continue
    if IRIDIUM_visible is None:
        IRIDIUM_visible = results[sat]["tolosat_visibility_OK"]
    else:
        IRIDIUM_visible = IRIDIUM_visible | results[sat]["tolosat_visibility_OK"]

time_limit = timedelta(hours=24)

fig, axes = pf.dark_figure()
axes[0].plot(results["timedelta"][results["timedelta"] < time_limit].dt.total_seconds() / 3600,
             IRIDIUM_visible[results["timedelta"] < time_limit], linestyle="none", marker=".")
axes[0].set_title("IRIDIUM satellites visibility from Tolosat")
axes[0].set_xlabel("Time [hours]")
axes[0].set_ylabel("Visibility")
axes[0].set_xlim(0, time_limit.total_seconds() / 3600)
pf.finish_dark_figure(fig, "IRIDIUM_visibility.png", show=True)
