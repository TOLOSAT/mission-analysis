from iridium_doppler import IRIDIUM_visibility, IRIDIUM_windows

from useful_functions import plot_functions as pf



# fig, axes = pf.dark_figure()
# axes[0].plot(results_dict["timedelta"].dt.total_seconds() / 86400, results_dict['IRIDIUM 100']["doppler_shift"])
# axes[0].set_title("Doppler shift of IRIDIUM 100")
# axes[0].set_xlabel("Time [days]")
# axes[0].set_ylabel("Doppler shift [Hz]")
# axes[0].set_xlim(0, max(results_dict["timedelta"].dt.total_seconds()) / 86400)
# pf.finish_dark_figure(fig, "IRIDIUM_100_doppler_shift.png", show=True)
#
# fig, axes = pf.dark_figure()
# axes[0].plot(results_dict["timedelta"].dt.total_seconds() / 86400, results_dict['IRIDIUM 100']["doppler_rate"])
# axes[0].set_title("Doppler rate of IRIDIUM 100")
# axes[0].set_xlabel("Time [days]")
# axes[0].set_ylabel("Doppler rate [Hz/s]")
# axes[0].set_xlim(0, max(results_dict["timedelta"].dt.total_seconds()) / 86400)
# pf.finish_dark_figure(fig, "IRIDIUM_100_doppler_rate.png", show=True)


fig, axes = pf.dark_figure()
axes[0].plot(IRIDIUM_visibility["seconds"] / 86400,
             IRIDIUM_visibility["sum_ok"], linestyle="none", marker=".")
axes[0].set_title("Visibility of IRIDIUM satellites satisfying all 4 conditions")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Number of satellites [-]")
axes[0].set_xlim(0, IRIDIUM_visibility["seconds"].max() / 86400)
pf.finish_dark_figure(fig, "IRIDIUM_visibility.png", show=True, force_y_int=True)

fig, axes = pf.dark_figure()
axes[0].vlines(IRIDIUM_windows['seconds'] / 86400, 0, IRIDIUM_windows['duration'] / 60)
axes[0].set_title("Visibility windows of at least one IRIDIUM satellite")
axes[0].set_xlabel("Time since launch [days]")
axes[0].set_ylabel("Window duration [mins]")
axes[0].set_ylim(0, IRIDIUM_windows['duration'].max() / 60)
axes[0].set_xlim(0, IRIDIUM_windows['seconds'].max() / 86400)
pf.finish_dark_figure(fig, "IRIDIUM_windows.png", show=True)

# mask = (results_dict["timedelta"] > timedelta(hours=2310, minutes=13)) & (
#         results_dict["timedelta"] <= timedelta(hours=2310, minutes=27))
# fig, axes = pf.dark_figure()
# axes[0].plot(results_dict["timedelta"].loc[mask].dt.total_seconds(),
#              results_dict["IRIDIUM 113"].loc[mask, "doppler_shift"].to_list(), linestyle="none",
#              marker=".")
# axes[0].set_title("Doppler shift of IRIDIUM 113")
# axes[0].set_xlabel("Time [seconds]")
# axes[0].set_ylabel("Doppler shift [Hz]")
# axes[0].set_xlim(min(results_dict["timedelta"].loc[mask].dt.total_seconds()),
#                  max(results_dict["timedelta"].loc[mask].dt.total_seconds()))
# pf.finish_dark_figure(fig, "IRIDIUM_all_ok_1day_doppler_shift.png", show=True)

# mask = (results_dict["timedelta"] > timedelta(hours=2325, minutes=10)) & (
#         results_dict["timedelta"] <= timedelta(hours=2335, minutes=13))
# fig, axes = pf.dark_figure()
# axes[0].plot(results_dict["timedelta"].loc[mask].dt.total_seconds(),
#              IRIDIUM_visibility.loc[mask, "sum_ok"].to_list(), linestyle="none",
#              marker=".")
# axes[0].set_title("Visibility of IRIDIUM satellites satisfying all 4 conditions")
# axes[0].set_xlabel("Time [seconds]")
# axes[0].set_ylabel("Number of satellites [-]")
# axes[0].set_xlim(min(results_dict["timedelta"].loc[mask].dt.total_seconds()),
#                  max(results_dict["timedelta"].loc[mask].dt.total_seconds()))
# pf.finish_dark_figure(fig, "IRIDIUM_all_ok_1day.png", show=True)
