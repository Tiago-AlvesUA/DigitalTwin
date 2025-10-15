# ------------------------------ #
# hono_arrivals - send_times_obu #
# ------------------------------ #

from datetime import datetime
import statistics

# --- File paths ---
send_file = "checkpoints/send_times.txt"
hono_file = "checkpoints/hono_arrivals.txt"

# --- Read timestamps ---
with open(send_file, "r") as f:
    send_times = [float(line.strip()) for line in f if line.strip()]

with open(hono_file, "r") as f:
    hono_times = [float(line.strip()) for line in f if line.strip()]

# --- Compute integer millisecond delays ---
delays = [int((hono_times[i] - send_times[i]) * 1000) for i in range(1000)]

# --- Print summary ---
print(f"Compared {len(delays)} messages")
print(f"Average delay: {statistics.mean(delays)} ms")
print(f"Min delay:     {min(delays)} ms")
print(f"Max delay:     {max(delays)} ms")
print(f"Std deviation: {statistics.stdev(delays)} ms")

# --- Save only delay values (integer ms) ---
with open("results/obu-to-hono-delays.csv", "w") as f:
    f.write("delay_milliseconds\n")
    for d in delays:
        f.write(f"{d}\n")

print(f"\nDelays saved to obu-to-hono-delays.csv")
