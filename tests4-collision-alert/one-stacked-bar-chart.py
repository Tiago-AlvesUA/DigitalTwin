# stacked_bar_delays_single.py
import matplotlib.pyplot as plt

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
        lines = f.readlines()[21:]  # skip header
    return [int(line.strip()) for line in lines]

# --- Read data ---
obu_agent = read_integers(file1)
coll_check_proc = read_integers(file2)
alert_ditto = read_integers(file3)
ditto_ws = read_integers(file4)
total = read_integers(file5)

# --- Compute averages for all 1000 samples ---
avg_obu_agent = sum(obu_agent) / len(obu_agent)
avg_coll_check_proc = sum(coll_check_proc) / len(coll_check_proc)
avg_alert_ditto = sum(alert_ditto) / len(alert_ditto)
avg_ditto_ws = sum(ditto_ws) / len(ditto_ws)

# --- Find best (min) and worst (max) total delay indices ---
best_idx = total.index(min(total))
worst_idx = total.index(max(total))

# --- Extract corresponding component delays ---
best_case = [
    obu_agent[best_idx],
    coll_check_proc[best_idx],
    alert_ditto[best_idx],
    ditto_ws[best_idx],
]

worst_case = [
    obu_agent[worst_idx],
    coll_check_proc[worst_idx],
    alert_ditto[worst_idx],
    ditto_ws[worst_idx],
]

# --- Plot a single stacked bar ---
plt.figure(figsize=(7, 6))
bar_width = 0.10

x_positions = [1, 1 + bar_width + 0.1, 1 + 2 * (bar_width + 0.1)]
labels = ["Best Case", "Average", "Worst Case"]

# Define colors
colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

def stacked_bar(x, values, label):
    plt.bar(x, values[0], width=bar_width, color=colors[0], label="NOS OBU → Agent" if label == "Average" else "")
    plt.bar(x, values[1], width=bar_width, bottom=values[0], color=colors[1], label="Collision Check" if label == "Average" else "")
    plt.bar(x, values[2], width=bar_width, bottom=values[0] + values[1], color=colors[2], label="Alert → Ditto" if label == "Average" else "")
    plt.bar(x, values[3], width=bar_width, bottom=sum(values[:3]), color=colors[3], label="Ditto → IT OBU" if label == "Average" else "")

# Plot bars
stacked_bar(x_positions[0], best_case, "Best Case")
stacked_bar(x_positions[1], [avg_obu_agent, avg_coll_check_proc, avg_alert_ditto, avg_ditto_ws], "Average")
stacked_bar(x_positions[2], worst_case, "Worst Case")

# --- Chart settings ---
plt.title("Stacked Delay Comparison (Best, Average, Worst Cases)")
plt.ylabel("Delay (ms)")
plt.xticks(x_positions, labels)
plt.xlim(0.8, 1 + 2 * (bar_width + 0.4))
plt.legend()
plt.tight_layout()

# Save and show
plt.savefig("charts/stacked-delays-single.png", dpi=300)
plt.show()
