import subprocess
import os
import pandas as pd
import re
import time
import psutil
import numpy as np

WORKLOAD_DIR = "../workloads/"
RESULT_DIR = "../results/raw/"
MINIMALLOC = "../miniMalloc.exe"

def parse_capacity(filename):
    m = re.search(r"cap(\d+)", filename)
    if not m:
        raise ValueError(f"Capacity missing in filename: {filename}")
    return int(m.group(1))
def run_one(csv_file):
    """Run MiniMalloc on a single CSV and collect extended metrics."""
    capacity = parse_capacity(csv_file)
    out_csv = os.path.join(RESULT_DIR, os.path.basename(csv_file))

    cmd = [
        MINIMALLOC,
        f"--capacity={capacity}",
        f"--input={csv_file}",
        f"--output={out_csv}"
    ]

    # Launch process with stdout/stderr suppressed
    with open(os.devnull, "w") as devnull:
        proc = subprocess.Popen(cmd, stdout=devnull, stderr=devnull)

        try:
            ps = psutil.Process(proc.pid)
        except psutil.NoSuchProcess:
            ps = None

        cpu_samples = []
        mem_samples = []

        # Prime CPU measurement
        if ps is not None:
            try:
                ps.cpu_percent(interval=None)
            except psutil.NoSuchProcess:
                ps = None

        t0 = time.perf_counter()

        # --- Sampling loop ---
        while True:
            # If process finished, stop sampling
            if proc.poll() is not None:
                break

            # CPU sample
            if ps is not None:
                try:
                    cpu_samples.append(ps.cpu_percent(interval=None))
                except psutil.NoSuchProcess:
                    ps = None

            # Memory sample
            if ps is not None:
                try:
                    mem_samples.append(ps.memory_info().rss)
                except psutil.NoSuchProcess:
                    ps = None

            time.sleep(0.01)

        t1 = time.perf_counter()
        elapsed_ms = (t1 - t0) * 1000

    # Load MiniMalloc output CSV
    df = pd.read_csv(out_csv)
    n_buffers = len(df)
    peak_offset = df["offset"].max()
    max_size = df["size"].max()
    min_size = df["size"].min()
    avg_size = df["size"].mean()

    # Compute additional metrics
    throughput = n_buffers / (elapsed_ms / 1000) if elapsed_ms > 0 else 0
    mem_efficiency = peak_offset / capacity if capacity else 0
    fragmentation = capacity - peak_offset

    avg_cpu = float(np.mean(cpu_samples)) if cpu_samples else 0.0
    max_cpu = float(np.max(cpu_samples)) if cpu_samples else 0.0
    cpu_std = float(np.std(cpu_samples)) if cpu_samples else 0.0

    max_rss = float(np.max(mem_samples)) if mem_samples else 0.0
    mem_std = float(np.std(mem_samples)) if mem_samples else 0.0

    return {
        "time_ms": elapsed_ms,
        "peak_offset": peak_offset,
        "avg_cpu": avg_cpu,
        "max_cpu": max_cpu,
        "cpu_std": cpu_std,
        "max_rss": max_rss,
        "mem_std": mem_std,
        "throughput": throughput,
        "mem_efficiency": mem_efficiency,
        "fragmentation": fragmentation,
        "max_size": max_size,
        "min_size": min_size,
        "avg_size": avg_size,
        "num_buffers": n_buffers,
        "capacity": capacity
    }

def extract_type_index(filename):
    """
    Extract workload type and numeric index from filenames like 'stress_11.cap123.csv'
    Returns a tuple: (type_order, index)
    """
    type_order_map = {"rand": 0, "stress": 1, "cnn": 2}
    
    # extract type prefix
    m_type = re.match(r'([a-zA-Z]+)_', filename)
    type_str = m_type.group(1) if m_type else ""
    type_order = type_order_map.get(type_str, 99)

    # extract numeric index
    m_index = re.search(r'_(\d+)', filename)
    index = int(m_index.group(1)) if m_index else float('inf')

    return (type_order, index)

def run_all():
    results = []

    # Ensure results directory exists
    os.makedirs(RESULT_DIR, exist_ok=True)
    os.makedirs(os.path.join("../results/processed/"), exist_ok=True)

    # List and sort CSVs
    csv_files = [f for f in os.listdir(WORKLOAD_DIR) if f.endswith(".csv")]
    csv_files.sort(key=extract_type_index)

    for file in csv_files:
        path = os.path.join(WORKLOAD_DIR, file)
        metrics = run_one(path)
        results.append([file] + list(metrics.values()))

    # Build DataFrame with all metric columns
    df = pd.DataFrame(
        results,
        columns=[
            "workload",
            "time_ms",
            "peak_offset",
            "avg_cpu",
            "max_cpu",
            "cpu_std",
            "max_rss",
            "mem_std",
            "throughput",
            "mem_efficiency",
            "fragmentation",
            "max_size",
            "min_size",
            "avg_size",
            "num_buffers",
            "capacity"
        ]
    )

    # Save summary CSV
    summary_csv = "../results/processed/summary.csv"
    df.to_csv(summary_csv, index=False)
    print(f"Saved benchmark summary to {summary_csv}")
    print(df)

if __name__ == "__main__":
    run_all()
