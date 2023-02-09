import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

no_tides = pd.read_csv("states_notides.csv", index_col=0)
tides = pd.read_csv("states_tides.csv", index_col=0)

state_difference = no_tides - tides
# difference norm
position_difference = np.linalg.norm(state_difference.iloc[:, 0:4].to_numpy(), axis=1)

plt.plot(position_difference)
plt.show()
