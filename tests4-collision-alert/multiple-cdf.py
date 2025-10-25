# cdf_delays.py
import matplotlib.pyplot as plt
import numpy as np

# Filenames
file1 = "results/mcm-reception-delays.csv"
file2 = "results/collision-check-delays.csv"
file3 = "results/checkcoll-to-ditto-delays.csv"
file4 = "results/ditto-to-ws-delays.csv"
file5 = "results/total-delays.csv"

# --- Helper function ---
def read_integers(filename):
    """Read integers from a CSV file, skipping the header."""
    with open(filename) as f:
        lines = f.readlines()[21:]  # TODO: change if needed (skip header and first 20 lines where collision check was not active)
    return np.array([int(line.strip()) for line in lines])

# --- Read data ---
obu_agent = read_integers(file1)
coll_check_proc = read_integers(file2)
alert_ditto = read_integers(file3)
ditto_ws = read_integers(file4)
total = read_integers(file5)

# --- Function to compute CDF ---
def compute_cdf(data):
    sorted_data = np.sort(data)
    cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    return sorted_data, cdf

# --- Compute CDFs ---
x1, y1 = compute_cdf(obu_agent)
x2, y2 = compute_cdf(coll_check_proc)
x3, y3 = compute_cdf(alert_ditto)
x4, y4 = compute_cdf(ditto_ws)
x5, y5 = compute_cdf(total)


# --- Plot ---
plt.figure(figsize=(10, 6))
plt.plot(x1, y1, label="OBU → Broker → Agent", linewidth=1.8, color="blue")
plt.plot(x2, y2, label="Collision Check", linewidth=1.8, color="orange")
plt.plot(x3, y3, label="Alert Generation → Ditto", linewidth=1.8, color="green")
plt.plot(x4, y4, label="Ditto → OBU(WS Client)", linewidth=1.8, color="red")
plt.plot(x5, y5, label="End-to-End Total Delay", linewidth=1.8, color="purple")

avg_total_delay = int(np.mean(total))
plt.axvline(x=avg_total_delay, color="purple", linestyle="--", linewidth=1.8, label=f"Average End-to-End Delay = {avg_total_delay} ms")

plt.title("CDF of Communication/Process Delays")
plt.xlabel("Delay (ms)")
plt.ylabel("Cumulative Probability")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.7)
plt.tight_layout()

#plt.xlim(0,200)

# Save and show
plt.savefig("charts/multiple-cdf-delays.png", dpi=300)
plt.show()
