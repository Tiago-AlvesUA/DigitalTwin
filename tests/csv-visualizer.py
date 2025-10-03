import pandas as pd
import matplotlib.pyplot as plt

# Write input CSV file path
file = input("Enter the path to the CSV file (e.g., results/latencies-mec-obu.csv): ")

data = pd.read_csv(file, skiprows=1, header=None, names=["latency_ms"])

# Box plot
plt.figure()
data.boxplot(column="latency_ms")
plt.ylabel("Latency (ms)")
plt.title("Box Plot of MEC→OBU Latency")
if file == "results/latencies-mec-obu.csv":
    plt.savefig("results/latency-alert-mec-obu_boxplot.png")
else:
    plt.savefig("results/latency-modemStatus-to-feature_boxplot.png")

# CDF
plt.figure()
sorted_vals = data["latency_ms"].sort_values()
cdf = sorted_vals.rank(method="first") / len(sorted_vals)
plt.plot(sorted_vals, cdf)
plt.xlabel("Latency (ms)")
plt.ylabel("CDF")
plt.title("CDF of MEC→OBU Latency")
plt.grid(True)
if file == "results/latencies-mec-obu.csv":
    plt.savefig("results/latency-alert-mec-obu_cdf.png")
else:
    # Max x-axis limit to 300 ms for better visualization
    plt.xlim(0, 300)
    plt.savefig("results/latency-modemStatus-to-feature_cdf.png")