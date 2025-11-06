# stacked_bar_delays_single.py
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

# --- Compute averages for all 1000 samples ---
avg_obu_hono = sum(obu_hono) / len(obu_hono)
avg_hono_ditto = sum(hono_ditto) / len(hono_ditto)
avg_ditto_ws = sum(ditto_ws) / len(ditto_ws)

# --- Find best (min) and worst (max) total delay indices ---
best_idx = total.index(min(total))
worst_idx = total.index(max(total))

# --- Extract corresponding component delays ---
best_case = [
    obu_hono[best_idx],
    hono_ditto[best_idx],
    ditto_ws[best_idx],
]

worst_case = [
    obu_hono[worst_idx],
    hono_ditto[worst_idx],
    ditto_ws[worst_idx],
]

# --- Plot a single stacked bar ---
plt.figure(figsize=(7, 6))
bar_width = 0.10

x_positions = [1, 1 + bar_width + 0.1, 1 + 2 * (bar_width + 0.1)]
labels = ["Best Case", "Average", "Worst Case"]

# Define colors
colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

def stacked_bar(x, values, label):
    plt.bar(x, values[0], width=bar_width, color=colors[0], label="Local Twin → Hono" if label == "Average" else "")
    plt.bar(x, values[1], width=bar_width, bottom=values[0], color=colors[1], label="Hono → Ditto" if label == "Average" else "")
    plt.bar(x, values[2], width=bar_width, bottom=values[0] + values[1], color=colors[2], label="Ditto → WS Client" if label == "Average" else "")

# Plot bars
stacked_bar(x_positions[0], best_case, "Best Case")
stacked_bar(x_positions[1], [avg_obu_hono, avg_hono_ditto, avg_ditto_ws], "Average")
stacked_bar(x_positions[2], worst_case, "Worst Case")

# --- Chart settings ---
plt.title("Stacked Delay Comparison (Best, Average, Worst Cases)")
plt.ylabel("Delay (ms)")
plt.xticks(x_positions, labels)
plt.xlim(0.8, 1 + 2 * (bar_width + 0.4))
plt.legend()
plt.tight_layout()

# Save and show
plt.savefig("day1/charts/stacked-delays-single.png", dpi=300)
plt.show()
