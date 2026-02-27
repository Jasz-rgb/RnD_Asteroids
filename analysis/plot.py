import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib.patheffects as pe

# =============================
# CONFIG
# =============================
SUMMARY_FILE = "results/analysis/unified/Unified_Model_Comparison_Advanced.csv"
PLOT_DIR = "results/analysis/plots"
os.makedirs(PLOT_DIR, exist_ok=True)

# =============================
# SCI-FI THEME
# =============================
def apply_scifi_theme():
    plt.style.use("dark_background")

    plt.rcParams.update({
        "figure.facecolor": "#0b0f1a",
        "axes.facecolor": "#0b0f1a",
        "axes.edgecolor": "#00f5ff",
        "axes.labelcolor": "#00f5ff",
        "xtick.color": "#00f5ff",
        "ytick.color": "#00f5ff",
        "grid.color": "#00f5ff",
        "text.color": "#00f5ff",
        "font.size": 11,
        "axes.titleweight": "bold",
        "axes.titlepad": 15,
        "axes.grid": True,
        "grid.alpha": 0.2,
        "grid.linestyle": "--"
    })

def neon_effect(artist, glow_color="#00f5ff"):
    artist.set_path_effects([
        pe.Stroke(linewidth=6, foreground=glow_color, alpha=0.3),
        pe.Normal()
    ])

apply_scifi_theme()

df = pd.read_csv(SUMMARY_FILE)

# ==========================================================
# 1️⃣ BETTER MODEL COUNT
# ==========================================================
fig, ax = plt.subplots(figsize=(6,5))
counts = df["better_model"].value_counts()

bars = ax.bar(
    counts.index,
    counts.values,
    color="#00f5ff",
    edgecolor="#00f5ff",
    alpha=0.8
)

ax.set_title("MODEL SUPERIORITY DISTRIBUTION")
ax.set_ylabel("ASTEROID COUNT")

for spine in ax.spines.values():
    spine.set_color("#00f5ff")

plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/better_model_distribution.png", dpi=300)
plt.close()

# ==========================================================
# 2️⃣ CLASS DISTRIBUTION (SIDE-BY-SIDE)
# ==========================================================
fig, ax = plt.subplots(figsize=(8,5))

manual_counts = df["manual_class"].value_counts()
rebound_counts = df["rebound_class"].value_counts()

classes = list(set(manual_counts.index).union(rebound_counts.index))

manual_vals = [manual_counts.get(c, 0) for c in classes]
rebound_vals = [rebound_counts.get(c, 0) for c in classes]

x = np.arange(len(classes))
width = 0.35

bars1 = ax.bar(
    x - width/2,
    manual_vals,
    width,
    label="Manual (GPU)",
    color="#00f5ff",
    alpha=0.8
)

bars2 = ax.bar(
    x + width/2,
    rebound_vals,
    width,
    label="Rebound",
    color="#ff00ff",
    alpha=0.8
)

ax.set_xticks(x)
ax.set_xticklabels(classes, rotation=30)
ax.set_ylabel("COUNT")
ax.set_title("BEHAVIOR CLASS COMPARISON")
ax.legend(frameon=False)

plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/behavior_class_comparison.png", dpi=300)
plt.close()

# ==========================================================
# 3️⃣ GROWTH RATIO DISTRIBUTION (LOG SCALE)
# ==========================================================
fig, ax = plt.subplots(figsize=(7,5))

ax.hist(
    df["manual_ratio"],
    bins=30,
    histtype="step",
    linewidth=2,
    color="#00f5ff",
    label="Manual (GPU)"
)

ax.hist(
    df["rebound_ratio"],
    bins=30,
    histtype="step",
    linewidth=2,
    color="#ff00ff",
    label="Rebound"
)

ax.set_xscale("log")
ax.set_xlabel("20-YEAR GROWTH RATIO (LOG SCALE)")
ax.set_ylabel("COUNT")
ax.set_title("ERROR GROWTH SPECTRUM")
ax.legend(frameon=False)

plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/growth_ratio_distribution.png", dpi=300)
plt.close()

# ==========================================================
# 4️⃣ VOLATILITY VS GROWTH (PHASE SPACE)
# ==========================================================
fig, ax = plt.subplots(figsize=(7,6))

colors = {
    "Stable": "#00ff88",
    "Mixed": "#ffaa00",
    "Runaway Divergence": "#ff0055"
}

for cls in df["manual_class"].unique():
    subset = df[df["manual_class"] == cls]
    ax.scatter(
        subset["manual_volatility"],
        subset["manual_ratio"],
        s=60,
        color=colors.get(cls, "#ffffff"),
        edgecolors="#00f5ff",
        alpha=0.85,
        label=cls
    )

ax.set_yscale("log")
ax.set_xlabel("MANUAL VOLATILITY INDEX")
ax.set_ylabel("MANUAL GROWTH RATIO (LOG)")
ax.set_title("ERROR DYNAMICS PHASE SPACE")
ax.legend(frameon=False)

plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/manual_phase_space.png", dpi=300)
plt.close()

# ==========================================================
# 5️⃣ RMS DIFFERENCE BETWEEN MODELS
# ==========================================================
df["rms_difference"] = df["manual_rms_error"] - df["rebound_rms_error"]

fig, ax = plt.subplots(figsize=(7,5))

ax.hist(
    df["rms_difference"],
    bins=30,
    histtype="stepfilled",
    color="#00f5ff",
    alpha=0.4,
    edgecolor="#00f5ff"
)

ax.axvline(0, color="#ff0055", linestyle="--", linewidth=2)

ax.set_xlabel("MANUAL RMS − REBOUND RMS (AU)")
ax.set_ylabel("COUNT")
ax.set_title("RMS ERROR DIFFERENCE DISTRIBUTION")

plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/rms_difference_distribution.png", dpi=300)
plt.close()

print("🚀 All sci-fi analysis plots saved to:", PLOT_DIR)