import pandas as pd
import numpy as np
import glob
import os
from scipy.stats import linregress

# =============================
# CONFIG
# =============================
REAL_DIR     = "results/real"
REBOUND_DIR  = "results/rebound"
MANUAL_DIR   = "results/manual"

OUTPUT_DIR   = "results/analysis/unified"
os.makedirs(OUTPUT_DIR, exist_ok=True)

ROLLING_WINDOW = 50
ANOMALY_Z = 3.0

# =============================
# HELPERS
# =============================
def magnitude(x, y, z):
    return np.sqrt(x**2 + y**2 + z**2)

def normalize_date(series):
    return pd.to_datetime(
        series.str.replace("A.D. ", "", regex=False)
    ).dt.date

summary = []

rebound_files = glob.glob(f"{REBOUND_DIR}/*_Rebound.csv")

for rebound_path in rebound_files:

    name = os.path.basename(rebound_path).replace("_Rebound.csv", "")

    real_path   = os.path.join(REAL_DIR, f"{name}_Real.csv")
    manual_path = os.path.join(MANUAL_DIR, f"{name}.csv")

    if not (os.path.exists(real_path) and os.path.exists(manual_path)):
        continue

    # --------------------------
    # LOAD DATA
    # --------------------------
    rebound = pd.read_csv(rebound_path)
    real    = pd.read_csv(real_path)
    manual  = pd.read_csv(manual_path)

    rebound["date"] = normalize_date(rebound["datetime_str"])
    real["date"]    = normalize_date(real["datetime_str"])
    manual["date"]  = pd.to_datetime(manual["date"]).dt.date

    # magnitudes
    rebound["r"] = magnitude(rebound.x, rebound.y, rebound.z)
    rebound["v"] = magnitude(rebound.vx, rebound.vy, rebound.vz)

    real["r"] = magnitude(real.x, real.y, real.z)
    real["v"] = magnitude(real.vx, real.vy, real.vz)

    manual["r"] = magnitude(manual.x, manual.y, manual.z)
    manual["v"] = magnitude(manual.vx, manual.vy, manual.vz)

    # --------------------------
    # MERGE ALL THREE
    # --------------------------
    df = real[["date","r","v"]].merge(
        rebound[["date","r","v"]],
        on="date",
        suffixes=("_real","_rebound")
    ).merge(
        manual[["date","r","v"]],
        on="date"
    )

    df.rename(columns={"r":"r_manual","v":"v_manual"}, inplace=True)

    if len(df) < 10:
        continue

    # --------------------------
    # ERROR COMPUTATION
    # --------------------------
    df["delta_r_rebound"] = abs(df["r_rebound"] - df["r_real"])
    df["delta_r_manual"]  = abs(df["r_manual"]  - df["r_real"])

    # --------------------------
    # METRIC FUNCTION
    # --------------------------
    def compute_metrics(series):
        rms = np.sqrt(np.mean(series**2))

        t = np.arange(len(series))
        slope, _, r_val, _, _ = linregress(t, series)
        r_squared = r_val**2

        ratio = series.iloc[-1] / series.iloc[0] if series.iloc[0] != 0 else 1
        volatility = series.std() / series.mean()

        return rms, ratio, volatility, r_squared

    rms_r_reb, ratio_reb, vol_reb, r2_reb = compute_metrics(df["delta_r_rebound"])
    rms_r_man, ratio_man, vol_man, r2_man = compute_metrics(df["delta_r_manual"])

    # --------------------------
    # BEHAVIOR CLASSIFIER
    # --------------------------
    def classify(ratio, volatility, r2):
        if ratio < 1.5 and volatility < 0.5:
            return "Stable"
        elif ratio < 3 and r2 > 0.7:
            return "Linear Drift"
        elif volatility > 1.0:
            return "Oscillatory"
        elif ratio >= 3:
            return "Runaway Divergence"
        else:
            return "Mixed"

    class_reb = classify(ratio_reb, vol_reb, r2_reb)
    class_man = classify(ratio_man, vol_man, r2_man)

    # --------------------------
    # SAVE PER OBJECT
    # --------------------------
    df.to_csv(
        f"{OUTPUT_DIR}/{name}_Detailed_Comparison.csv",
        index=False
    )

    summary.append({
        "object": name,

        "rebound_rms_error": rms_r_reb,
        "manual_rms_error": rms_r_man,

        "rebound_ratio": ratio_reb,
        "manual_ratio": ratio_man,

        "rebound_volatility": vol_reb,
        "manual_volatility": vol_man,

        "rebound_class": class_reb,
        "manual_class": class_man,

        "better_model": "Manual (GPU)" if rms_r_man < rms_r_reb else "Rebound"
    })

# --------------------------
# SAVE SUMMARY
# --------------------------
summary_df = pd.DataFrame(summary)
summary_df.to_csv(
    f"{OUTPUT_DIR}/Unified_Model_Comparison_Advanced.csv",
    index=False
)

print("Unified advanced comparison complete.")