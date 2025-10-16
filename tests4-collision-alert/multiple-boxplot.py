# boxplot_delays.py
import matplotlib.pyplot as plt

# Filenames
file1 = "day1/results/mcm-reception-delays.csv"
file2 = "day1/results/collision-check-delays.csv"
file3 = "day1/results/checkcoll-to-ditto-delays.csv"
file4 = "day1/results/ditto-to-ws-delays.csv"
file5 = "day1/results/total-delays.csv"

# --- Helper function ---
def read_integers(filename):
    """Read integers from a CSV file, skipping the header."""
    with open(filename) as f:
        lines = f.readlines()[18:]  # TODO: change if needed (skip header and first 17 lines where collision check was not active)
    return [int(line.strip()) for line in lines]

# --- Read data ---
obu_agent = read_integers(file1)
coll_check_proc = read_integers(file2)
alert_ditto = read_integers(file3)
ditto_ws = read_integers(file4)
total = read_integers(file5)

# --- Prepare data for box plot ---
data = [obu_agent, coll_check_proc, alert_ditto, ditto_ws, total]
labels = ["OBU → MEC(Broker → Agent)", "Collision Check", "Alert Generation → Ditto", "MEC(Ditto) → OBU(WS)", "Total Delay"]

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
plt.savefig("day1/charts/multiple-boxplot-delays.png", dpi=300)
plt.show()
