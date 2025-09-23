import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("results/latencies-mec-obu.csv", skiprows=1, header=None, names=["latency_ms"])

# Box plot
plt.figure()
data.boxplot(column="latency_ms")
plt.ylabel("Latency (ms)")
plt.title("Box Plot of MEC→OBU Latency")
plt.savefig("results/latency_boxplot.png")

# CDF
plt.figure()
sorted_vals = data["latency_ms"].sort_values()
cdf = sorted_vals.rank(method="first") / len(sorted_vals)
plt.plot(sorted_vals, cdf)
plt.xlabel("Latency (ms)")
plt.ylabel("CDF")
plt.title("CDF of MEC→OBU Latency")
plt.grid(True)
plt.savefig("results/latency_cdf.png")