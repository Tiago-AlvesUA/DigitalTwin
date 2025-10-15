# stacked_bar_delays_single.py
import matplotlib.pyplot as plt

# Filenames
file1 = "day1/results/obu-to-hono-delays.csv"
file2 = "day1/results/hono-to-ditto-delays.csv"
file3 = "day1/results/ditto-to-ws-delays.csv"

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

# --- Compute averages for all 1000 samples ---
avg_obu_hono = sum(obu_hono) / len(obu_hono)
avg_hono_ditto = sum(hono_ditto) / len(hono_ditto)
avg_ditto_ws = sum(ditto_ws) / len(ditto_ws)

# --- Plot a single stacked bar ---
plt.figure(figsize=(5, 6))
bar_width = 0.05

plt.bar(1, avg_obu_hono, width=bar_width, label="Obu → Hono Delay", color="#1f77b4")
plt.bar(1, avg_hono_ditto, width=bar_width, bottom=avg_obu_hono, label="Hono → Ditto Delay", color="#ff7f0e")
plt.bar(1, avg_ditto_ws, width=bar_width, bottom=avg_obu_hono + avg_hono_ditto, label="Ditto → WS Delay", color="#2ca02c")

# --- Chart settings ---
plt.title("Average Stacked Delay for 1000 Messages")
plt.ylabel("Average Delay (ms)")
plt.xticks([1], ["Overall Average"])

plt.xlim(0.9, 1.25)

plt.legend()
plt.tight_layout()

# Save and show
plt.savefig("day1/charts/stacked-delays-single.png", dpi=300)
plt.show()
