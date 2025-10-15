import pandas as pd
import matplotlib.pyplot as plt

# Write input CSV file path
file = input("Enter the path to the CSV file (e.g., results/latencies-mec-obu.csv): ")

data = pd.read_csv(file, skiprows=1, header=None, names=["latency_ms"])
data.columns = data.columns.str.strip()

# Box plot
plt.figure()
data.boxplot(column="latency_ms")
#data.boxplot(column="delay_ms")
plt.ylabel("Latency (ms)")
if file == "results/latencies-mec-obu.csv":
    plt.title("Box Plot of MEC→OBU Latency")
    plt.savefig("results/latency-alert-mec-obu_boxplot.png")
else:
    plt.title("Box Plot of OBU→Feature Update Latency")
    #plt.ylim(0, 100)  # Limit y-axis to 300 ms for better visualization
    plt.savefig("charts/latency-modemStatus-to-feature_boxplot.png")

# CDF
plt.figure()
sorted_vals = data["latency_ms"].sort_values()
#sorted_vals = data["delay_ms"].sort_values()
cdf = sorted_vals.rank(method="first") / len(sorted_vals)
plt.plot(sorted_vals, cdf)
plt.xlabel("Latency (ms)")
plt.ylabel("CDF")
plt.grid(True)
if file == "results/latencies-mec-obu.csv":
    plt.title("CDF of MEC→OBU Latency")
    plt.savefig("results/latency-alert-mec-obu_cdf.png")
else:
    plt.title("CDF of OBU→Feature Update Latency")
    # Max x-axis limit to 300 ms for better visualization
    #plt.xlim(0, 100)
    plt.savefig("charts/latency-modemStatus-to-feature_cdf.png")