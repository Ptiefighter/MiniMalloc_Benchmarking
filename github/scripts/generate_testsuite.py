import os
import csv
import random

# Compute peak memory usage
def compute_capacity(rows):
    """
    rows: list of [id, lower, upper, size]
    Returns the peak memory usage (sum of overlapping buffers)
    """
    events = []
    for _, lower, upper, size in rows:
        events.append((lower, size))   # allocation
        events.append((upper, -size))  # deallocation
    events.sort()
    max_usage = 0
    current_usage = 0
    for _, change in events:
        current_usage += change
        if current_usage > max_usage:
            max_usage = current_usage
    return max_usage

# Output directory for CSV files
WORKLOAD_DIR = "../workloads/"
os.makedirs(WORKLOAD_DIR, exist_ok=True)

# ----------------------------
# Random buffer workloads
# ----------------------------
def generate_random_buffers(prefix, n_buffers=100, size_min=4, size_max=32, lifetime_max=100):
    rows = []
    for i in range(n_buffers):
        lower = random.randint(0, lifetime_max // 2)
        upper = random.randint(lower + 1, lifetime_max)
        size = random.randint(size_min, size_max)
        rows.append([f"b{i}", lower, upper, size])
    
    capacity = compute_capacity(rows)
    filename = f"{prefix}.cap{capacity}.csv"
    path = os.path.join(WORKLOAD_DIR, filename)
    
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id","lower","upper","size"])
        writer.writerows(rows)
    
    print(f"Generated {path} with capacity {capacity}")
    return filename, capacity

# ----------------------------
# CNN-like structured workloads
# ----------------------------
def generate_cnn_like(prefix, layers=50, lifetime_jitter=3):
    """
    CNN-like allocation with staggered lifetimes to simulate pipelined execution.
    Each layer creates:
      - feature map: lives slightly longer
      - workspace: temporary buffer during computation
    lifetime_jitter: max random offset for start/end times
    """
    rows = []
    buf_id = 0
    t = 0  # time counter
    for l in range(layers):
        # Feature map
        size_f = random.randint(32, 128) * (l+1)
        lower_f = t + random.randint(0, lifetime_jitter)
        upper_f = lower_f + 3 + random.randint(0, lifetime_jitter)
        rows.append([f"f{buf_id}", lower_f, upper_f, size_f])
        buf_id += 1

        # Workspace
        size_w = random.randint(64, 256) * (l+1)
        lower_w = lower_f + random.randint(0, 1)  # workspace starts during feature map
        upper_w = lower_w + 2 + random.randint(0, lifetime_jitter)
        rows.append([f"w{buf_id}", lower_w, upper_w, size_w])
        buf_id += 1

        # Increment global time to simulate sequential layers
        t = lower_f + 1

    # Compute peak memory usage for MiniMalloc
    capacity = compute_capacity(rows)
    filename = f"{prefix}.cap{capacity}.csv"
    path = os.path.join(WORKLOAD_DIR, filename)

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "lower", "upper", "size"])
        writer.writerows(rows)

    print(f"Generated {path} with capacity {capacity}, {len(rows)} buffers")
    return filename, capacity

# ----------------------------
# Synthetic stress workloads
# ----------------------------
def generate_stress(prefix, n_buffers=200, max_overlap=0.9):
    """
    Generates buffers with high overlap to stress MiniMalloc
    """
    rows = []
    max_lifetime = 100
    for i in range(n_buffers):
        lower = random.randint(0, int(max_lifetime*max_overlap))
        upper = random.randint(lower+1, max_lifetime)
        size = random.randint(4, 128)
        rows.append([f"s{i}", lower, upper, size])
    capacity = compute_capacity(rows)
    filename = f"{prefix}.cap{capacity}.csv"
    path = os.path.join(WORKLOAD_DIR, filename)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id","lower","upper","size"])
        writer.writerows(rows)
    print(f"Generated {path} with capacity {capacity}")
    return filename, capacity

# ----------------------------
# Generate the full suite with loops
# ----------------------------
if __name__ == "__main__":
    # Random workloads: 25 → 300 buffers in steps of 25
    counter = 1
    for n in range(25, 301, 25):
        generate_random_buffers(f"rand_{counter}", n_buffers=n)
        counter += 1
    
    # Stress workloads: 25 → 300 buffers in steps of 25
    counter = 1
    for n in range(25, 301, 25):
        generate_stress(f"stress_{counter}", n_buffers=n, max_overlap=0.9)
        counter += 1

    # CNN workloads: make them increasingly deep to reach 200+ buffers
    cnn_layers_list = [10, 25, 50, 75, 100]  # 2 buffers per layer → 20→200 buffers
    counter = 1
    for layers in cnn_layers_list:
        generate_cnn_like(f"cnn_{counter}", layers=layers)
        counter += 1
