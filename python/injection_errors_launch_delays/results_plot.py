import pandas as pd
import matplotlib.pyplot as plt

from useful_functions import get_orbit

df = pd.read_csv('Tolosat_states.csv')
print(df.columns)
fig, axs = plt.subplots(2,3)
fig.suptitle('Evolution of Keplerian Elements throughout the mission')
df["semi_major_axis"].plot(ax=axs[0,0])
axs[0, 0].set_title('Semi-Major Axis')
df["eccentricity"].plot(ax=axs[0,1])
axs[0, 1].set_title('Eccentricity')
df["inclination"].plot(ax=axs[0,2])
axs[0, 2].set_title('Inclination')
df["argument_of_periapsis"].plot(ax=axs[1,0])
axs[1, 0].set_title('Argument of Periapsis')
df["longitude_of_ascending_node"].plot(ax=axs[1,1])
axs[1, 1].set_title('Longitude of Ascending Node')
df["true_anomaly"].plot(ax=axs[1,2])
axs[1, 2].set_title('True Anomaly')
plt.show()


orbit_name = "SSO6_plus_injection_error"
Tolosat_orbit = get_orbit(orbit_name)
print(Tolosat_orbit["semi_major_axis"])