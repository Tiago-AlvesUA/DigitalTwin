# cdf_delays.py
import matplotlib.pyplot as plt
import numpy as np

# Filenames
file1 = "day1/results/obu-to-hono-delays.csv"
file2 = "day1/results/hono-to-ditto-delays.csv"
file3 = "day1/results/ditto-to-ws-delays.csv"
file4 = "day1/results/total-delays.csv"

# --- Helper function ---
def read_integers(filename):
    """Read integers from a CSV file, skipping the header."""
    with open(filename) as f:
        lines = f.readlines()[1:]  # skip header
    return np.array([int(line.strip()) for line in lines])

# --- Read data ---
obu_hono = read_integers(file1)
hono_ditto = read_integers(file2)
ditto_ws = read_integers(file3)
total = read_integers(file4)

# --- Function to compute CDF ---
def compute_cdf(data):
    sorted_data = np.sort(data)
    cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    return sorted_data, cdf

# --- Compute CDFs ---
x1, y1 = compute_cdf(obu_hono)
x2, y2 = compute_cdf(hono_ditto)
x3, y3 = compute_cdf(ditto_ws)
x4, y4 = compute_cdf(total)

# --- Plot ---
plt.figure(figsize=(10, 6))
plt.plot(x1, y1, label="Obu → Hono", linewidth=1.8, color="blue")
plt.plot(x2, y2, label="Hono → Ditto", linewidth=1.8, color="orange")
plt.plot(x3, y3, label="Ditto → WS", linewidth=1.8, color="green")
plt.plot(x4, y4, label="Total Delay", linewidth=1.8, color="purple")

plt.title("CDF of Communication/Process Delays")
plt.xlabel("Delay (ms)")
plt.ylabel("Cumulative Probability")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.7)
plt.tight_layout()

#plt.xlim(0,200)

# Save and show
plt.savefig("cdf-delays.png", dpi=300)
plt.show()
