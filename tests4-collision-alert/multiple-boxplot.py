# boxplot_delays.py
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
    return [int(line.strip()) for line in lines]

# --- Read data ---
obu_agent = read_integers(file1)
coll_check_proc = read_integers(file2)
alert_ditto = read_integers(file3)
ditto_ws = read_integers(file4)
total = read_integers(file5)

# --- Prepare data for box plot ---
data = [obu_agent, coll_check_proc, alert_ditto, ditto_ws, total]
labels = ["OBU → Broker → Agent", "Collision Check", "Alert Generation → Ditto", "Ditto → OBU(WS Client)", "End-to-End Total Delay"]

# --- Compute statistics ---
print("Delay Statistics (in ms):")
print("-" * 60)
for label, values in zip(labels, data):
    values = np.array(values)
    median = np.median(values)
    q1 = np.percentile(values, 25)
    q3 = np.percentile(values, 75)
    iqr = q3 - q1
    minimum = np.min(values)
    maximum = np.max(values)
    print(f"{label}:")
    print(f"  Median: {median:.2f} ms")
    print(f"  IQR (Q3 - Q1): {iqr:.2f} ms  [Q1={q1:.2f}, Q3={q3:.2f}]")
    print(f"  Min: {minimum:.2f} ms,  Max: {maximum:.2f} ms\n")



# --- Plot ---
plt.figure(figsize=(10, 6))
plt.boxplot(data, labels=labels, patch_artist=True)

plt.title("Delay Distribution Across Communication/Processing Stages")
plt.ylabel("Delay (ms)")

# Optional styling for colors
colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#cc1f1f", "#9467bd"]
for patch, color in zip(plt.gca().artists, colors):
    patch.set_facecolor(color)

plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()

# Save and show
plt.savefig("charts/multiple-boxplot-delays.png", dpi=300)
plt.show()
