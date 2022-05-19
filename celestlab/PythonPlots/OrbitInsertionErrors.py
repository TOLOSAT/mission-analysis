# Preamble
from math import pi
from PlotFunctions import *

target_folder = "OrbitInsertionErrors"
data_path = get_plot_path(target_folder)

cjd = np.array(open_csv(data_path, "cjd_stela.csv")).transpose()
cjd0 = np.array(open_csv(data_path, "cjd0.csv")).transpose()
ecc = np.array(open_csv(data_path, "ecc_stela.csv")).transpose()
inc = np.array(open_csv(data_path, "inc_stela.csv")).transpose()
mltan = np.array(open_csv(data_path, "mltan.csv")).transpose()
pom = np.array(open_csv(data_path, "pom_stela.csv")).transpose()
RAAN = np.array(open_csv(data_path, "RAAN_stela.csv")).transpose()
sma = np.array(open_csv(data_path, "sma_stela.csv")).transpose()
eclipses = np.array(open_csv(data_path, "eclipse_duration_umb.csv")).transpose()
labels = open_csv(data_path, "legend_name.csv", is_string=True)
source_labels = [ii.replace('Â', '') for ii in labels]

earthRadius = 6.3781e6

# Figures
tmp_xTime = (cjd - cjd0) / 365.25


def plot1(axes_, source_labels_):
    axes_[0].plot(tmp_xTime, eclipses / 60, label='dummy label')
    plt.xlim([0, axes_[0].get_xlim()[1]])
    plt.ylim([0, axes_[0].get_ylim()[1]])
    plt.xlabel("Time [years]")
    plt.ylabel("Eclipse duration per orbit [min]")
    plt.title("Evolution of the eclipse duration over the entire mission \n for maximum insertion errors")
    handles_, _ = axes_[0].get_legend_handles_labels()
    handles_, labels_ = flip_legend(2, False, handles_, source_labels_)
    return handles_, labels_


fig, axes = dark_figure(figsize=(7, 6))
handles, labels = plot1(axes, source_labels)
fig.legend(handles, labels, loc=(0.015, 0.04), ncol=2, frameon=False, labelcolor='white')
finish_dark_figure(fig, target_folder + '/' + target_folder + '_Eclipses_dark.png', show=True)

fig, axes = light_figure(figsize=(7, 6))
handles, labels = plot1(axes, source_labels)
fig.legend(handles, labels, loc=(0.015, 0.04), ncol=2, frameon=False, labelcolor='black')
finish_light_figure(fig, target_folder + '/' + target_folder + '_Eclipses_light.png', show=True)


def plot2(axes_, source_labels_):
    handles_ = []
    for ii in range(len(labels)):
        axes_[0].plot(tmp_xTime, (sma[:, ii] - earthRadius) / 1e3)
        axes_[1].plot(tmp_xTime, inc[:, ii] * 180 / pi)
        axes_[2].plot(tmp_xTime, ecc[:, ii])
        axes_[3].plot(tmp_xTime, pom[:, ii] * 180 / pi)
        axes_[4].plot(tmp_xTime, RAAN[:, ii] * 180 / pi)
        axes_[5].plot(tmp_xTime, mltan[:, ii], label='dummy label')
    for jj in range(6):
        axes_[jj].set(xlabel="Time [years]", xlim=[0, axes_[jj].get_xlim()[1]])
    axes_[0].set(ylabel="Altitude [km]")
    axes_[1].set(ylabel="Inclination [deg]")
    axes_[2].set(ylabel="Eccentricity [-]")
    axes_[3].set(ylabel="Argument of perigee [deg]")
    axes_[4].set(ylabel="RAAN [deg]")
    axes_[5].set(ylabel="MLTAN [hours]")
    handles_, _ = axes_[5].get_legend_handles_labels()
    handles_, labels_ = flip_legend(2, False, handles_, source_labels_)
    return handles_, labels_


F2, axes = dark_figure(subplots=(2, 3), figsize=(10, 6.5))
plot2(axes, source_labels)
plt.suptitle("Evolution of orbital parameters during the entire mission for maximum insertion errors", color='white')
F2.legend(handles, labels, loc=(0.015, 0.055), ncol=2, frameon=False,
          labelcolor='white')
finish_dark_figure(F2, target_folder + '/' + target_folder + '_OrbitalParameters_dark.png', show=True)
print("done")

F2, axes = light_figure(subplots=(2, 3), figsize=(10, 6.5))
plot2(axes, source_labels)
plt.suptitle("Evolution of orbital parameters during the entire mission for maximum insertion errors", color='black')
F2.legend(handles, labels, loc=(0.015, 0.055), ncol=2, frameon=False,
          labelcolor='black')
finish_light_figure(F2, target_folder + '/' + target_folder + '_OrbitalParameters_light.png', show=True)
print("done")
