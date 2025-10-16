# ------------------------------ #
# ditto_arrivals - check_collision_done #
# ------------------------------ #

from datetime import datetime, timezone
import statistics

# --- File paths ---
checkColl_file = "checkpoints/check-collision-done-times.txt"
ditto_file = "checkpoints/ditto-receive-times.txt"

# --- Read Hono timestamps (already UNIX floats) ---
with open(checkColl_file, "r") as f:
    checkColl_times = [float(line.strip()) for line in f if line.strip()]

# --- Read Ditto timestamps (ISO8601 -> convert to UNIX seconds) ---
def parse_ditto_time(line):
    # remove timezone offset for parsing
    dt = datetime.fromisoformat(line.strip().replace("Z", "+00:00")).timestamp()
    print("Parsed Ditto time:", dt)
    return dt

with open(ditto_file, "r") as f:
    ditto_times = [parse_ditto_time(line) for line in f if line.strip()]

# --- Compute per-message delay ---
delays = [int((ditto_times[i] - checkColl_times[i]) * 1000) for i in range(1000)]

print("FIRST check-collision UTC:", datetime.utcfromtimestamp(checkColl_times[0]))

print("LAST check-collision UTC:", datetime.utcfromtimestamp(checkColl_times[1000-1]))
#print("First ditto-receive UTC:", datetime.utcfromtimestamp(ditto_times[0]))


# --- Print summary statistics ---
print(f"Compared 1000 messages")
print(f"Average delay: {statistics.mean(delays)} ms")
print(f"Min delay:     {min(delays)} ms")
print(f"Max delay:     {max(delays)} ms")
print(f"Std deviation: {statistics.stdev(delays)} ms")

# --- Optionally save to CSV ---
with open("results/checkcoll-to-ditto-delays.csv", "w") as f:
    f.write("delay_milliseconds\n")
    for d in delays:
        f.write(f"{d}\n")

print("\nDelays saved to checkcoll-to-ditto-delays.csv")
