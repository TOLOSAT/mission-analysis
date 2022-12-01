from datetime import timedelta

from iridium_doppler import results, IRIDIUM_visibility
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

fig, axes = pf.dark_figure()
axes[0].plot(results["timedelta"].dt.total_seconds() / 86400, IRIDIUM_visibility["sum_ok"].to_list(), linestyle="none",
             marker=".")
axes[0].set_title("Visibility of IRIDIUM satellites satisfying all 4 conditions")
axes[0].set_xlabel("Time [days]")
axes[0].set_ylabel("Number of satellites [-]")
axes[0].set_xlim(0, max(results["timedelta"].dt.total_seconds()) / 86400)
pf.finish_dark_figure(fig, "IRIDIUM_all_ok.png", show=True)

mask = (results["timedelta"] > timedelta(hours=2310, minutes=13)) & (
        results["timedelta"] <= timedelta(hours=2310, minutes=27))
fig, axes = pf.dark_figure()
axes[0].plot(results["timedelta"].loc[mask].dt.total_seconds(),
             results["IRIDIUM 113"].loc[mask, "doppler_shift"].to_list(), linestyle="none",
             marker=".")
axes[0].set_title("Doppler shift of IRIDIUM 113")
axes[0].set_xlabel("Time [seconds]")
axes[0].set_ylabel("Doppler shift [Hz]")
axes[0].set_xlim(min(results["timedelta"].loc[mask].dt.total_seconds()),
                 max(results["timedelta"].loc[mask].dt.total_seconds()))
pf.finish_dark_figure(fig, "IRIDIUM_all_ok_1day_doppler_shift.png", show=True)


mask = (results["timedelta"] > timedelta(hours=2325, minutes=10)) & (
        results["timedelta"] <= timedelta(hours=2335,minutes=13))
fig, axes = pf.dark_figure()
axes[0].plot(results["timedelta"].loc[mask].dt.total_seconds(),
             IRIDIUM_visibility.loc[mask, "sum_ok"].to_list(), linestyle="none",
             marker=".")
axes[0].set_title("Visibility of IRIDIUM satellites satisfying all 4 conditions")
axes[0].set_xlabel("Time [seconds]")
axes[0].set_ylabel("Number of satellites [-]")
axes[0].set_xlim(min(results["timedelta"].loc[mask].dt.total_seconds()), max(results["timedelta"].loc[mask].dt.total_seconds()))
pf.finish_dark_figure(fig, "IRIDIUM_all_ok_1day.png", show=True)

for sat in results:
    if "IRIDIUM" not in sat:
        continue
    if any(results[sat].loc[mask,"all_OK"]):
        print(sat)
        print(results["datetime"].loc[mask].loc[results[sat].loc[mask,"all_OK"]].to_list())
