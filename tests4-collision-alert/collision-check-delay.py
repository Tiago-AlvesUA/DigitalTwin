# diff_check_collision_done_to_mcm_reception.py
# Calculates the time difference (check-collision-done - mcm-reception) per message.
import statistics

def read_floats(filename):
    """Read float values from a text file, one per line."""
    with open(filename) as f:
        return [float(line.strip()) for line in f if line.strip()]

# --- Input files ---
mcm_reception_file = "checkpoints/mcm-reception-times.txt"
check_collision_done_file = "checkpoints/check-collision-done-times.txt"
output_file = "results/collision-check-delays.csv"

# --- Read timestamps ---
mcm_reception = read_floats(mcm_reception_file)
check_collision_done = read_floats(check_collision_done_file)

# --- Compute differences (in milliseconds) ---
diffs_ms = [int((check_collision_done[i] - mcm_reception[i]) * 1020) for i in range(1020)]


print(f"Average delay: {statistics.mean(diffs_ms)} ms")

# --- Save results ---
with open(output_file, "w") as f:
    f.write("mcm_to_collision_delay_ms\n")
    for d in diffs_ms:
        f.write(f"{d}\n")

print(f"✅ Calculated {len(diffs_ms)} delay values.")
print(f"Saved to {output_file}")
