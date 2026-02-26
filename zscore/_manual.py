import pandas as pd
import numpy as np
import glob
import os

# =============================
# CONFIG
# =============================
MANUAL_DIR  = "results/manual"
REAL_DIR    = "results/real"
REBOUND_DIR = "results/rebound"

OUTPUT_DIR  = "results/zscore"
Z_THRESHOLD = 2.5

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =============================
# HELPERS
# =============================
def magnitude(x, y, z):
    return np.sqrt(x**2 + y**2 + z**2)

def normalize_date(series):
    return pd.to_datetime(
        series.str.replace("A.D. ", "", regex=False)
    ).dt.date

# =============================
# LOAD + MERGE
# =============================
merged_objects = {}

manual_files = glob.glob(f"{MANUAL_DIR}/*.csv")

for manual_path in manual_files:
    name = os.path.basename(manual_path).replace(".csv", "")

    real_name = name.replace("_", " ")
    real_path = f"{REAL_DIR}/{real_name}_Real.csv"
    rebound_path = f"{REBOUND_DIR}/{name}_Rebound.csv"

    if not (os.path.exists(real_path) and os.path.exists(rebound_path)):
        continue

    manual  = pd.read_csv(manual_path)
    real    = pd.read_csv(real_path)
    rebound = pd.read_csv(rebound_path)

    # ---- normalize dates ----
    manual["date"]  = pd.to_datetime(manual["date"]).dt.date
    real["date"]    = normalize_date(real["datetime_str"])
    rebound["date"] = normalize_date(rebound["datetime_str"])

    # ---- magnitudes ----
    manual["r_manual"] = magnitude(manual.x, manual.y, manual.z)
    manual["v_manual"] = magnitude(manual.vx, manual.vy, manual.vz)

    real["r_real"] = magnitude(real.x, real.y, real.z)
    real["v_real"] = magnitude(real.vx, real.vy, real.vz)

    rebound["r_rebound"] = magnitude(rebound.x, rebound.y, rebound.z)
    rebound["v_rebound"] = magnitude(rebound.vx, rebound.vy, rebound.vz)

    # ---- merge ----
    df = manual[["date","r_manual","v_manual"]].merge(
         real[["date","r_real","v_real"]], on="date"
    ).merge(
         rebound[["date","r_rebound","v_rebound"]], on="date"
    )

    if len(df) == 0:
        continue

    # ---- physical errors ----
    df["delta_r_kepler"] = abs(df["r_manual"] - df["r_real"])
    df["delta_v_kepler"] = abs(df["v_manual"] - df["v_real"])

    merged_objects[name] = df

# =============================
# LOCAL Z-SCORE + SUMMARY
# =============================
summary = []

for name, df in merged_objects.items():

    # ---- LOCAL statistics ----
    mu_dr  = df["delta_r_kepler"].mean()
    std_dr = df["delta_r_kepler"].std()

    mu_dv  = df["delta_v_kepler"].mean()
    std_dv = df["delta_v_kepler"].std()

    # Prevent divide-by-zero
    if std_dr == 0:
        df["z_r"] = 0
    else:
        df["z_r"] = abs(df["delta_r_kepler"] - mu_dr) / std_dr

    if std_dv == 0:
        df["z_v"] = 0
    else:
        df["z_v"] = abs(df["delta_v_kepler"] - mu_dv) / std_dv

    df["z_score"] = np.maximum(df["z_r"], df["z_v"])
    df["anomaly"] = (df["z_score"] >= Z_THRESHOLD).astype(int)

    # ---- save per-object file ----
    df.to_csv(f"{OUTPUT_DIR}/{name}_ZScore.csv", index=False)

    # =============================
    # EXPLAINABILITY
    # =============================
    vel_dom = ((df["anomaly"] == 1) & (df["z_v"] > df["z_r"])).sum()
    pos_dom = ((df["anomaly"] == 1) & (df["z_r"] >= df["z_v"])).sum()
    total_anom = int(df["anomaly"].sum())

    if total_anom == 0:
        dominant_mode = "None"
    elif pos_dom > vel_dom:
        dominant_mode = "Position"
    else:
        dominant_mode = "Velocity"

    if total_anom >= 3:
        temporal = "Persistent"
    elif total_anom > 0:
        temporal = "Isolated"
    else:
        temporal = "None"

    if dominant_mode == "Position":
        explanation = "Long-term orbital geometry deviation"
    elif dominant_mode == "Velocity":
        explanation = "Short-term dynamical instability"
    else:
        explanation = "Consistent with reference ephemeris"

    max_z = df["z_score"].max()

    if total_anom == 0:
        stability = "Stable"
    elif max_z < 4.0:
        stability = "Marginally Stable"
    else:
        stability = "Unstable"

    summary.append({
        "object": name,
        "max_z_score": max_z,
        "anomaly_count": total_anom,
        "velocity_dominated_anomalies": int(vel_dom),
        "position_dominated_anomalies": int(pos_dom),
        "dominant_error_mode": dominant_mode,
        "temporal_behavior": temporal,
        "physical_interpretation": explanation,
        "stability_class": stability
    })

# =============================
# SAVE SUMMARY
# =============================
pd.DataFrame(summary).to_csv(
    f"{OUTPUT_DIR}/ZScore_Summary_XAI.csv", index=False
)

print("LOCAL Z-score anomaly analysis complete.")