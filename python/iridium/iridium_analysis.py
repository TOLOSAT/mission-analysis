from datetime import timedelta

from iridium_doppler import results_dict, IRIDIUM_visibility, IRIDIUM_windows
from useful_functions import plot_functions as pf

fig, axes = pf.dark_figure()
axes[0].plot(results_dict["timedelta"].dt.total_seconds() / 86400, results_dict['IRIDIUM 100']["doppler_shift"])
axes[0].set_title("Doppler shift of IRIDIUM 100")
axes[0].set_xlabel("Time [days]")
axes[0].set_ylabel("Doppler shift [Hz]")
axes[0].set_xlim(0, max(results_dict["timedelta"].dt.total_seconds()) / 86400)
pf.finish_dark_figure(fig, "IRIDIUM_100_doppler_shift.png", show=True)

fig, axes = pf.dark_figure()
axes[0].plot(results_dict["timedelta"].dt.total_seconds() / 86400, results_dict['IRIDIUM 100']["doppler_rate"])
axes[0].set_title("Doppler rate of IRIDIUM 100")
axes[0].set_xlabel("Time [days]")
axes[0].set_ylabel("Doppler rate [Hz/s]")
axes[0].set_xlim(0, max(results_dict["timedelta"].dt.total_seconds()) / 86400)
pf.finish_dark_figure(fig, "IRIDIUM_100_doppler_rate.png", show=True)

IRIDIUM_visible = None
for sat in results_dict:
    if "IRIDIUM" not in sat:
        continue
    if IRIDIUM_visible is None:
        IRIDIUM_visible = results_dict[sat]["tolosat_visibility_OK"]
    else:
        IRIDIUM_visible = IRIDIUM_visible | results_dict[sat]["tolosat_visibility_OK"]

time_limit = timedelta(hours=24)

fig, axes = pf.dark_figure()
axes[0].plot(results_dict["timedelta"][results_dict["timedelta"] < time_limit].dt.total_seconds() / 3600,
             IRIDIUM_visible[results_dict["timedelta"] < time_limit], linestyle="none", marker=".")
axes[0].set_title("IRIDIUM satellites visibility from Tolosat")
axes[0].set_xlabel("Time [hours]")
axes[0].set_ylabel("Visibility")
axes[0].set_xlim(0, time_limit.total_seconds() / 3600)
pf.finish_dark_figure(fig, "IRIDIUM_visibility.png", show=True)

fig, axes = pf.dark_figure()
axes[0].plot(results_dict["timedelta"].dt.total_seconds() / 86400, IRIDIUM_visibility["sum_ok"].to_list(), linestyle="none",
             marker=".")
axes[0].set_title("Visibility of IRIDIUM satellites satisfying all 4 conditions")
axes[0].set_xlabel("Time [days]")
axes[0].set_ylabel("Number of satellites [-]")
axes[0].set_xlim(0, max(results_dict["timedelta"].dt.total_seconds()) / 86400)
pf.finish_dark_figure(fig, "IRIDIUM_all_ok.png", show=True)

mask = (results_dict["timedelta"] > timedelta(hours=2310, minutes=13)) & (
        results_dict["timedelta"] <= timedelta(hours=2310, minutes=27))
fig, axes = pf.dark_figure()
axes[0].plot(results_dict["timedelta"].loc[mask].dt.total_seconds(),
             results_dict["IRIDIUM 113"].loc[mask, "doppler_shift"].to_list(), linestyle="none",
             marker=".")
axes[0].set_title("Doppler shift of IRIDIUM 113")
axes[0].set_xlabel("Time [seconds]")
axes[0].set_ylabel("Doppler shift [Hz]")
axes[0].set_xlim(min(results_dict["timedelta"].loc[mask].dt.total_seconds()),
                 max(results_dict["timedelta"].loc[mask].dt.total_seconds()))
pf.finish_dark_figure(fig, "IRIDIUM_all_ok_1day_doppler_shift.png", show=True)

mask = (results_dict["timedelta"] > timedelta(hours=2325, minutes=10)) & (
        results_dict["timedelta"] <= timedelta(hours=2335, minutes=13))
fig, axes = pf.dark_figure()
axes[0].plot(results_dict["timedelta"].loc[mask].dt.total_seconds(),
             IRIDIUM_visibility.loc[mask, "sum_ok"].to_list(), linestyle="none",
             marker=".")
axes[0].set_title("Visibility of IRIDIUM satellites satisfying all 4 conditions")
axes[0].set_xlabel("Time [seconds]")
axes[0].set_ylabel("Number of satellites [-]")
axes[0].set_xlim(min(results_dict["timedelta"].loc[mask].dt.total_seconds()),
                 max(results_dict["timedelta"].loc[mask].dt.total_seconds()))
pf.finish_dark_figure(fig, "IRIDIUM_all_ok_1day.png", show=True)

for sat in results_dict:
    if "IRIDIUM" not in sat:
        continue
    if any(results_dict[sat].loc[mask, "all_OK"]):
        print(sat)
        print(results_dict["datetime"].loc[mask].loc[results_dict[sat].loc[mask, "all_OK"]].to_list())

fig, axes = pf.dark_figure()
axes[0].vlines(IRIDIUM_windows['elapsed'].dt.total_seconds() / 86400, 0, IRIDIUM_windows['duration'] / 60)
axes[0].set_title("Visibility windows of at least one IRIDIUM satellite")
axes[0].set_xlabel("Elapsed time [days]")
axes[0].set_ylabel("Window duration [mins]")
axes[0].set_ylim(0, IRIDIUM_windows['duration'].max() / 60)
axes[0].set_xlim(0, max(IRIDIUM_windows['elapsed'].tail(1).dt.total_seconds() / 86400))
pf.finish_dark_figure(fig, "IRIDIUM_windows.png", show=True)
