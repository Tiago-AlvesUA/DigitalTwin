# boxplot_delays.py
import matplotlib.pyplot as plt

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
labels = ["Obu → Hono", "Hono → Ditto", "Ditto → WS", "Total Delay"]

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
plt.savefig("boxplot-delays.png", dpi=300)
plt.show()
