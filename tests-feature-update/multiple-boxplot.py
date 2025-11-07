# boxplot_delays.py
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
    return [int(line.strip()) for line in lines]

# --- Read data ---
obu_hono = read_integers(file1)
hono_ditto = read_integers(file2)
ditto_ws = read_integers(file3)
total = read_integers(file4)

# --- Prepare data for box plot ---
data = [obu_hono, hono_ditto, ditto_ws, total]
labels = ["Local Twin → Hono", "Hono → Ditto", "Ditto → WS Client", "End-to-End Total Delay"]

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
colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd"]
for patch, color in zip(plt.gca().artists, colors):
    patch.set_facecolor(color)

plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()

# Save and show
plt.savefig("day1/charts/multiple-boxplot-delays.png", dpi=300)
plt.show()
