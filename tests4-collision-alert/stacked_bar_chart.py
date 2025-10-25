# stacked_bar_delays_grouped.py
import matplotlib.pyplot as plt

# Filenames
file1 = "results/mcm-reception-delays.csv"
file2 = "results/collision-check-delays.csv"
file3 = "results/checkcoll-to-ditto-delays.csv"
file4 = "results/ditto-to-ws-delays.csv"

# --- Helper function ---
def read_integers(filename):
    """Read integers from a CSV file, skipping the header."""
    with open(filename) as f:
        lines = f.readlines()[21:]  # skip header
    return [int(line.strip()) for line in lines]

def group_average(values, n):
    """Return list of average values for groups of size n."""
    return [sum(values[i:i+n]) / n for i in range(0, len(values), n)]

# --- Read data ---
obu_agent = read_integers(file1)
coll_check_proc = read_integers(file2)
alert_ditto = read_integers(file3)
ditto_ws = read_integers(file4)

# --- X-axis labels (message group index) ---
messages = list(range(1, len(obu_agent) + 1))

# --- Plot stacked bar chart ---
plt.figure(figsize=(12, 6))
plt.bar(messages, obu_agent, label="OBU → Broker → Agent", color="#1f77b4")
plt.bar(messages, coll_check_proc, bottom=obu_agent, label="Collision Check", color="#ff7f0e")
plt.bar(messages, alert_ditto,
        bottom=[a + b for a, b in zip(obu_agent, coll_check_proc)],
        label="Alert Generation → Ditto", color="#2ca02c")
plt.bar(messages, ditto_ws,
        bottom=[a + b + c for a, b, c in zip(obu_agent, coll_check_proc, alert_ditto)],
        label="Ditto → OBU(WS Client)", color="#d62728")


plt.title("Per-Message Stacked Delay")
plt.xlabel("Message Index")
plt.ylabel("Delay (ms)")
plt.legend()
plt.tight_layout()

# Save and show
plt.savefig("charts/stacked-delays.png", dpi=300)
plt.show()
