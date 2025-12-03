import csv
import os

def compute_capacity(rows):
    """
    Compute peak memory usage = max sum of overlapping buffer sizes
    """
    events = []
    for _, lower, upper, size in rows:
        events.append((lower, size))    # allocation
        events.append((upper, -size))   # deallocation

    events.sort()
    max_usage = 0
    current_usage = 0
    for _, change in events:
        current_usage += change
        if current_usage > max_usage:
            max_usage = current_usage
    return max_usage

def generate_mm_csv(prefix, n_buffers=50):
    rows = []

    for i in range(n_buffers):
        lower = 0
        upper = 10 * (i + 1)        # fake lifetime
        size = 4 * (i % 8 + 1)      # sizes vary 4–32 bytes
        rows.append([f"b{i}", lower, upper, size])

    # compute capacity using overlapping buffer sizes
    capacity = compute_capacity(rows)

    # output path: prefix.cap<capacity>.csv
    filename = f"{prefix}.cap{capacity}.csv"
    path = os.path.join("../workloads/", filename)

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "lower", "upper", "size"])
        writer.writerows(rows)

    print(f"Generated {path} with capacity={capacity}")
    return filename, capacity

if __name__ == "__main__":
    generate_mm_csv("mm_small", 100)
    generate_mm_csv("mm_medium", 500)