# Preamble
import matplotlib.pylab as pl
from math import pi
from PlotFunctions import *

target_folder = "LaunchYearMissionDuration"
data_path = get_plot_path(target_folder)

cjd = np.array(open_csv(data_path, "cjd_stela.csv")).transpose()
cjd0 = np.array(open_csv(data_path, "cjd0.csv")).transpose()
ecc = np.array(open_csv(data_path, "ecc.csv")).transpose()
inc = np.array(open_csv(data_path, "inc.csv")).transpose()
mltan = np.array(open_csv(data_path, "mltan.csv")).transpose()
pom = np.array(open_csv(data_path, "pom.csv")).transpose()
RAAN = np.array(open_csv(data_path, "RAAN.csv")).transpose()
sma = np.array(open_csv(data_path, "sma.csv")).transpose()
years = np.array(open_csv(data_path, "years.csv")).transpose()
earthRadius = 6.3781e6

# colors = np.array([(0, 135, 108), (61, 154, 112), (100, 173, 115), (137, 191, 119), (175, 209, 124), (214, 225, 132),
#                    (255, 241, 143), (253, 213, 118), (251, 184, 98), (245, 155, 86), (238, 125, 79), (227, 94, 78),
#                    (212, 61, 81)]) / 255.0
colors = pl.cm.jet(np.linspace(0, 1, len(years)))


# Figures
def plot1(axes_):
    handles_ = []
    for ii in range(len(years)):
        tmp_xTime = (cjd[:, ii] - cjd0[ii]) / 365.25
        color = colors[ii]
        axes_[0].plot(tmp_xTime, (sma[:, ii] - earthRadius) / 1e3, color=color)
        axes_[1].plot(tmp_xTime, inc[:, ii] * 180 / pi, color=color)
        axes_[2].plot(tmp_xTime, ecc[:, ii], color=color)
        axes_[3].plot(tmp_xTime, pom[:, ii] * 180 / pi, color=color)
        axes_[4].plot(tmp_xTime, RAAN[:, ii] * 180 / pi, color=color)
        axes_[5].plot(tmp_xTime, mltan[:, ii], color=color, label='dummy label')
    for jj in range(6):
        axes_[jj].set(xlabel="Time [years]", xlim=[0, axes_[jj].get_xlim()[1]])
    axes[0].set(ylabel="Altitude [km]")
    axes[1].set(ylabel="Inclination [deg]")
    axes[2].set(ylabel="Eccentricity [-]")
    axes[3].set(ylabel="Argument of perigee [deg]")
    axes[4].set(ylabel="RAAN [deg]")
    axes[5].set(ylabel="MLTAN [hours]")
    handles_, _ = axes[5].get_legend_handles_labels()
    handles_, labels_ = flip_legend(7, False, handles_, [str(int(x)) for x in flatten(years.tolist())])
    return handles_, labels_


fig, axes = dark_figure(subplots=(2, 3), figsize=(10, 6.5))
handles, labels = plot1(axes)
plt.suptitle("Evolution of orbital parameters during the entire mission for various launch years", color='white')
fig.legend(handles, labels, loc=(0.015, 0.055), ncol=7, frameon=False,
           labelcolor='white')
finish_dark_figure(fig, target_folder + '/' + 'launchYearMissionDuration_dark.png', show=True)

fig, axes = light_figure(subplots=(2, 3), figsize=(10, 6.5))
handles, labels = plot1(axes)
plt.suptitle("Evolution of orbital parameters during the entire mission for various launch years", color='black')
fig.legend(handles, labels, loc=(0.015, 0.055), ncol=7, frameon=False,
           labelcolor='black')
finish_light_figure(fig, target_folder + '/' + 'launchYearMissionDuration_light.png', show=True)
print("done")
