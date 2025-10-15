# --------------------------------- #
# ws_receive-times - ditto_arrivals #
# --------------------------------- #

from datetime import datetime
import statistics

# --- File paths ---
ditto_file = "checkpoints/ditto_arrivals.txt"
ws_receive_file = "checkpoints/ws-receive-times.txt"

# --- Read Hono timestamps (already UNIX floats) ---
with open(ws_receive_file, "r") as f:
    ws_receive_times = [float(line.strip()) for line in f if line.strip()]

# --- Read Ditto timestamps (ISO8601 -> convert to UNIX seconds) ---
def parse_ditto_time(line):
    # remove timezone offset for parsing
    return datetime.fromisoformat(line.strip().replace("Z", "+00:00")).timestamp()

with open(ditto_file, "r") as f:
    ditto_times = [parse_ditto_time(line) for line in f if line.strip()]

# --- Compute per-message delay ---
delays = [int((ws_receive_times[i] - ditto_times[i]) * 1000) for i in range(1000)]

# --- Print summary statistics ---
print(f"Compared 100 messages")
print(f"Average delay: {statistics.mean(delays)} ms")
print(f"Min delay:     {min(delays)} ms")
print(f"Max delay:     {max(delays)} ms")
print(f"Std deviation: {statistics.stdev(delays)} ms")

# --- Optionally save to CSV ---
with open("results/ditto-to-ws-delays.csv", "w") as f:
    f.write("delay_milliseconds\n")
    for d in delays:
        f.write(f"{d}\n")

print("\nDelays saved to ditto-to-delays.csv")
