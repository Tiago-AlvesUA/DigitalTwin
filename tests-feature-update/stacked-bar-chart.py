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

# --- X-axis labels (message group index) ---
messages = list(range(1, len(obu_hono) + 1))

# --- Plot stacked bar chart ---
plt.figure(figsize=(12, 6))
plt.bar(messages, obu_hono, label="Local Twin → Hono")#, color="red")
plt.bar(messages, hono_ditto, bottom=obu_hono, label="Hono → Ditto")#, color="green")
plt.bar(messages, ditto_ws,
        bottom=[a + b for a, b in zip(obu_hono, hono_ditto)],
        label="Ditto → WS Client")#, color="blue")

plt.title("Per-Message Stacked Delay")
plt.xlabel("Message Index")
plt.ylabel("Delay (ms)")
plt.legend()
plt.tight_layout()

# Save and show
plt.savefig("day1/charts/stacked-delays.png", dpi=300)
plt.show()
