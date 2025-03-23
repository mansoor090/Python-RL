import pandas as pd
import matplotlib.pyplot as plt

# Load Monitor logs (adjust the file name/path as necessary)
df = pd.read_csv("../test_monitor.monitor.csv", skiprows=1)  # The first row is metadata
# Assuming 'r' is the column for rewards and 'l' for episode lengths
plt.figure()
plt.plot(df["l"], df["r"])
plt.xlabel("Episode Length")
plt.ylabel("Reward")
plt.title("Training Reward Progress")
plt.show()