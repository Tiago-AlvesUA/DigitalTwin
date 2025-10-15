# stacked_bar_delays_grouped.py
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

def group_average(values, n):
    """Return list of average values for groups of size n."""
    return [sum(values[i:i+n]) / n for i in range(0, len(values), n)]

# --- Read data ---
obu_hono = read_integers(file1)
hono_ditto = read_integers(file2)
ditto_ws = read_integers(file3)

# --- Grouping ---
group_size = 10  # adjust as needed (e.g., 5, 20, 50)
obu_hono_avg = group_average(obu_hono, group_size)
hono_ditto_avg = group_average(hono_ditto, group_size)
ditto_ws_avg = group_average(ditto_ws, group_size)

# --- X-axis labels (message group index) ---
messages = list(range(1, len(obu_hono_avg) + 1))

# --- Plot stacked bar chart ---
plt.figure(figsize=(12, 6))
plt.bar(messages, obu_hono_avg, label="Obu → Hono Delay")#, color="red")
plt.bar(messages, hono_ditto_avg, bottom=obu_hono_avg, label="Hono → Ditto Delay")#, color="green")
plt.bar(messages, ditto_ws_avg,
        bottom=[a + b for a, b in zip(obu_hono_avg, hono_ditto_avg)],
        label="Ditto → WS Delay")#, color="blue")

plt.title(f"Average Stacked Delay per {group_size} Messages")
plt.xlabel(f"Message Group (x{group_size})")
plt.ylabel("Average Delay (ms)")
plt.legend()
plt.tight_layout()

# Save and show
plt.savefig("day1/charts/stacked-delays-grouped.png", dpi=300)
plt.show()
