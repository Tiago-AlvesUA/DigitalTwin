# stacked_bar_delays_single.py
import matplotlib.pyplot as plt

# Filenames
file1 = "day1/results/mcm-reception-delays.csv"
file2 = "day1/results/collision-check-delays.csv"
file3 = "day1/results/checkcoll-to-ditto-delays.csv"
file4 = "day1/results/ditto-to-ws-delays.csv"

# --- Helper function ---
def read_integers(filename):
    """Read integers from a CSV file, skipping the header."""
    with open(filename) as f:
        lines = f.readlines()[18:]  # skip header
    return [int(line.strip()) for line in lines]

# --- Read data ---
obu_agent = read_integers(file1)
coll_check_proc = read_integers(file2)
alert_ditto = read_integers(file3)
ditto_ws = read_integers(file4)

# --- Compute averages for all 1000 samples ---
avg_obu_agent = sum(obu_agent) / len(obu_agent)
avg_coll_check_proc = sum(coll_check_proc) / len(coll_check_proc)
avg_alert_ditto = sum(alert_ditto) / len(alert_ditto)
avg_ditto_ws = sum(ditto_ws) / len(ditto_ws)

# --- Plot a single stacked bar ---
plt.figure(figsize=(5, 6))
bar_width = 0.05

plt.bar(1, avg_obu_agent, width=bar_width, label="OBU → MEC(Broker → Agent)", color="#1f77b4")
plt.bar(1, avg_coll_check_proc, width=bar_width, bottom=avg_obu_agent, label="Collision Check", color="#ff7f0e")
plt.bar(1, avg_alert_ditto, width=bar_width, bottom=avg_obu_agent + avg_coll_check_proc, label="Alert Generation → Ditto", color="#2ca02c")
plt.bar(1, avg_ditto_ws, width=bar_width, bottom=avg_obu_agent + avg_coll_check_proc + avg_alert_ditto, label="MEC(Ditto) → OBU(WS)", color="#d62728")

# --- Chart settings ---
plt.title("Average Stacked Delay for ~1000 Messages")
plt.ylabel("Average Delay (ms)")
plt.xticks([1], ["Overall Average"])

plt.xlim(0.9, 1.25)

plt.legend()
plt.tight_layout()

# Save and show
plt.savefig("day1/charts/stacked-delays-single.png", dpi=300)
plt.show()
