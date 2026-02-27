import os
import pandas as pd

BASE_DIR = r"C:\Users\JASMINE\Desktop\RnD_asteroid"

GPU_SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "results",
    "zscore",
    "_manual",
    "ZScore_Summary_XAI.csv"
)

REBOUND_SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "results",
    "zscore",
    "_rebound",
    "Rebound_vs_Real_Summary.csv"
)

OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "results",
    "zscore",
    "model_comparison_summary.csv"
)
# =============================
# LOAD SUMMARIES
# =============================
gpu_df = pd.read_csv(GPU_SUMMARY_PATH)
rebound_df = pd.read_csv(REBOUND_SUMMARY_PATH)

# Rename columns for clarity
gpu_df = gpu_df.rename(columns={
    "max_z_score": "gpu_max_z",
    "anomaly_count": "gpu_anomaly_count",
    "stability_class": "gpu_stability_class",
    "mean_delta_r": "gpu_mean_delta_r",
    "mean_delta_v": "gpu_mean_delta_v"
})

rebound_df = rebound_df.rename(columns={
    "max_z_score": "rebound_max_z",
    "anomaly_count": "rebound_anomaly_count",
    "stability_class": "rebound_stability_class",
    "mean_delta_r": "rebound_mean_delta_r",
    "mean_delta_v": "rebound_mean_delta_v"
})

# =============================
# MERGE
# =============================
comparison = gpu_df.merge(rebound_df, on="object", how="inner")

# =============================
# PERFORMANCE METRICS
# =============================

# Absolute improvement (positive = Rebound better)
comparison["delta_mean_r_difference"] = (
    comparison["gpu_mean_delta_r"] - comparison["rebound_mean_delta_r"]
)

comparison["delta_mean_v_difference"] = (
    comparison["gpu_mean_delta_v"] - comparison["rebound_mean_delta_v"]
)

# Percentage improvement
comparison["r_improvement_percent"] = (
    comparison["delta_mean_r_difference"] /
    comparison["gpu_mean_delta_r"] * 100
)

comparison["v_improvement_percent"] = (
    comparison["delta_mean_v_difference"] /
    comparison["gpu_mean_delta_v"] * 100
)

# =============================
# BETTER MODEL CLASSIFICATION
# =============================
def better_model(row):
    if row["rebound_mean_delta_r"] < row["gpu_mean_delta_r"]:
        return "Rebound"
    elif row["rebound_mean_delta_r"] > row["gpu_mean_delta_r"]:
        return "GPU"
    else:
        return "Equal"

comparison["better_model_radial"] = comparison.apply(better_model, axis=1)

# =============================
# SAVE RESULT
# =============================
comparison.to_csv(OUTPUT_PATH, index=False)

print("Model comparison complete.")
print(f"Saved to: {OUTPUT_PATH}")

# =============================
# QUICK OVERALL STATS
# =============================
print("\n===== Overall Performance Summary =====")

avg_gpu_r = comparison["gpu_mean_delta_r"].mean()
avg_rebound_r = comparison["rebound_mean_delta_r"].mean()

print(f"Average GPU radial error:      {avg_gpu_r:.6f} AU")
print(f"Average Rebound radial error:  {avg_rebound_r:.6f} AU")

if avg_rebound_r < avg_gpu_r:
    print("Overall winner: Rebound")
else:
    print("Overall winner: GPU")