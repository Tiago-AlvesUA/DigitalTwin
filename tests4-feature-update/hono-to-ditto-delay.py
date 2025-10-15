# ------------------------------ #
# ditto_arrivals - hono_arrivals #
# ------------------------------ #

from datetime import datetime
import statistics

# --- File paths ---
hono_file = "checkpoints/hono_arrivals.txt"
ditto_file = "checkpoints/ditto_arrivals.txt"

# --- Read Hono timestamps (already UNIX floats) ---
with open(hono_file, "r") as f:
    hono_times = [float(line.strip()) for line in f if line.strip()]

# --- Read Ditto timestamps (ISO8601 -> convert to UNIX seconds) ---
def parse_ditto_time(line):
    # remove timezone offset for parsing
    return datetime.fromisoformat(line.strip().replace("Z", "+00:00")).timestamp()

with open(ditto_file, "r") as f:
    ditto_times = [parse_ditto_time(line) for line in f if line.strip()]

# --- Compute per-message delay ---
delays = [int((ditto_times[i] - hono_times[i]) * 1000) for i in range(1000)]

# --- Print summary statistics ---
print(f"Compared 100 messages")
print(f"Average delay: {statistics.mean(delays)} ms")
print(f"Min delay:     {min(delays)} ms")
print(f"Max delay:     {max(delays)} ms")
print(f"Std deviation: {statistics.stdev(delays)} ms")

# --- Optionally save to CSV ---
with open("results/hono-to-ditto-delays.csv", "w") as f:
    f.write("delay_milliseconds\n")
    for d in delays:
        f.write(f"{d}\n")

print("\nDelays saved to hono-to-ditto-delays.csv")
