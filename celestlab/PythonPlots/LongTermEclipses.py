# Preamble
from math import pi
from PlotFunctions import *

target_folder = "LongTermEclipses"
data_path = get_plot_path(target_folder)

stela_datevector = open_csv(data_path, "stela_datevector.csv")
stela_eclipses = open_csv(data_path, "stela_eclipses.csv")
stela_mean_kep = open_csv(data_path, "stela_mean_kep.csv")


# Figures
def plot1():
    plt.plot(stela_datevector - stela_datevector[0], stela_eclipses / 60)
    plt.xlim([0, max(stela_datevector - stela_datevector[0])])
    plt.ylim([0, max(stela_eclipses) * 1.1 / 60])
    plt.xlabel("Days since beginning of mission")
    plt.ylabel("Eclipse duration per orbit [min]")
    plt.title("Evolution of the eclipse duration over the entire mission")


F1, _ = dark_figure()
plot1()
finish_dark_figure(F1, target_folder + '/' + 'long_term_eclipses_dark.png', show=True)

F1, _ = light_figure()
plot1()
finish_light_figure(F1, target_folder + '/' + 'long_term_eclipses_light.png', show=True)


def plot2(axes_):
    axes_[0].plot(stela_datevector - stela_datevector[0], stela_mean_kep[:, 0])
    axes_[0].set(ylabel="SMA")
    axes_[1].plot(stela_datevector - stela_datevector[0], stela_mean_kep[:, 2] * 180 / pi)
    axes_[1].set(ylabel="Inclination [deg]")
    axes_[2].plot(stela_datevector - stela_datevector[0], stela_mean_kep[:, 1])
    axes_[2].set(ylabel="Eccentricity [-]")
    axes_[3].plot(stela_datevector - stela_datevector[0], stela_mean_kep[:, 3] * 180 / pi)
    axes_[3].set(ylabel="Argument of perigee [deg]")
    axes_[4].plot(stela_datevector - stela_datevector[0], stela_mean_kep[:, 4] * 180 / pi)
    axes_[4].set(ylabel="RAAN [deg]")
    axes_[5].plot(stela_datevector - stela_datevector[0], stela_mean_kep[:, 5] * 180 / pi)
    axes_[5].set(ylabel="Mean anomaly [deg]")


F2, axes = dark_figure(subplots=(2, 3), figsize=(10, 5))
plot2(axes)
plt.suptitle("Evolution of orbital parameters over the entire mission", color='white')
finish_dark_figure(F2, target_folder + '/' + 'long_term_orbit_dark.png', show=True)

F2, axes = light_figure(subplots=(2, 3), figsize=(10, 5))
plot2(axes)
plt.suptitle("Evolution of orbital parameters over the entire mission", color='black')
finish_light_figure(F2, target_folder + '/' + 'long_term_orbit_white.png', show=True)
