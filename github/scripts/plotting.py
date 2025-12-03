import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import os

RESULT_CSV = "../results/processed/summary.csv"
PDF_PATH = "../results/plots/benchmark_summary.pdf"

os.makedirs(os.path.dirname(PDF_PATH), exist_ok=True)

df = pd.read_csv(RESULT_CSV)

# Use the DataFrame index as x-axis
df['row_index'] = df.index

sns.set_theme(style="whitegrid", palette="deep", font_scale=1.2)

with PdfPages(PDF_PATH) as pdf:

    # -------------------------
    # Helper function
    # -------------------------
    def save_lineplot(y, ylabel, title, logy=False):
        plt.figure(figsize=(11,6))
        sns.lineplot(
            data=df, x='row_index', y=y,
            marker='o', linewidth=2, markersize=7
        )
        plt.title(title)
        plt.xlabel("Row Index")
        plt.ylabel(ylabel)
        if logy:
            plt.yscale("log")
        plt.tight_layout()
        pdf.savefig()
        plt.close()

    # --- Plot 1: Allocation Time ---
    save_lineplot("time_ms", "Time (ms)", "Allocation Time vs Row Index")

    # --- Plot 2: Peak Memory Offset ---
    save_lineplot("peak_offset", "Peak Offset", "Peak Memory Offset vs Row Index")

    # --- Plot 3: Peak RSS Memory ---
    save_lineplot("max_rss", "Peak RSS (Bytes)", "Peak RSS Memory Usage vs Row Index", logy=True)

    # --- Plot 4: Throughput ---
    save_lineplot("throughput", "Throughput (ops/sec)", "Throughput vs Row Index", logy=True)

    # --- Plot 5: Memory Efficiency ---
    save_lineplot("mem_efficiency", "Memory Efficiency", "Memory Efficiency vs Row Index")

    # --- Plot 6: Fragmentation ---
    save_lineplot("fragmentation", "Fragmentation", "Fragmentation vs Row Index")

    # --- Plot 7: CPU Usage (Avg & Max) ---
    plt.figure(figsize=(11,6))
    sns.lineplot(data=df, x='row_index', y='avg_cpu', marker='o', linewidth=2, markersize=7, label="avg_cpu")
    sns.lineplot(data=df, x='row_index', y='max_cpu', marker='x', linestyle='--', linewidth=2, label="max_cpu")
    plt.title("CPU Usage vs Row Index")
    plt.xlabel("Row Index")
    plt.ylabel("CPU Usage (%)")
    plt.tight_layout()
    pdf.savefig()
    plt.close()

    # --- Plot 8: Buffer Size Stats ---
    plt.figure(figsize=(11,6))
    df_melted = df.melt(
        id_vars=["row_index"],
        value_vars=["min_size", "avg_size", "max_size"],
        var_name="metric",
        value_name="size",
    )
    sns.lineplot(
        data=df_melted,
        x='row_index',
        y='size',
        hue='metric',
        marker='o',
        linewidth=2,
        markersize=7
    )
    plt.title("Buffer Size Statistics vs Row Index")
    plt.xlabel("Row Index")
    plt.ylabel("Size (bytes)")
    plt.tight_layout()
    pdf.savefig()
    plt.close()

print(f"Saved all plots to PDF: {PDF_PATH}")