
import pandas as pd
import matplotlib.pyplot as plt

keplerian_df = pd.read_csv("Tolosat_states.csv")

# Extract the epoch and semi-major axis columns
epochs = keplerian_df["epoch"]
semi_major_axis = keplerian_df["semi_major_axis"]

# Plot semi-major axis as a function of epoch
plt.figure(figsize=(10, 6))
plt.plot(epochs, semi_major_axis, label="Semi-Major Axis", linewidth=2)
plt.xlabel("Epoch (s since J2000)")
plt.ylabel("Semi-Major Axis (m)")
plt.title("Semi-Major Axis vs. Epoch")
plt.legend()
plt.grid(True)

# Display the plot
plt.show()