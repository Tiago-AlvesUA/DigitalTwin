# sum_lines.py
# Sums each line of three files with equal line counts (1000 lines each)
# Skips header line, assumes all values are integers

# File names
file1 = "results/obu-to-hono-delays.csv"
file2 = "results/hono-to-ditto-delays.csv"
file3 = "results/ditto-to-ws-delays.csv"
output_file = "results/total-delays.csv"

# Open all files and process line by line
with open(file1, "r") as f1, open(file2, "r") as f2, open(file3, "r") as f3, open(output_file, "w") as out:
    # Skip header line
    header1 = f1.readline()
    header2 = f2.readline()
    header3 = f3.readline()
    
    # Write a header for clarity (optional)
    out.write("total_delay\n")
    
    # Process remaining lines
    for line1, line2, line3 in zip(f1, f2, f3):
        # Convert to integers and sum
        val1 = int(line1.strip())
        val2 = int(line2.strip())
        val3 = int(line3.strip())
        
        total = val1 + val2 + val3
        out.write(f"{total}\n")

print(f"Summed integer values written to {output_file}")
