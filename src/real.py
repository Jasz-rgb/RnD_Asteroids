import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import numpy as np
import matplotlib.pyplot as plt
from astroquery.jplhorizons import Horizons

# ---------- Read targets from file ----------
targets_file = r"C:/Users/JASMINE/Desktop/RnD_asteroid/targets_english.txt"

asteroids = []

with open(targets_file, "r", encoding="utf-8") as f:
    for line in f:
        name = line.strip()
        if name:
            asteroids.append(name)

print(f"[INFO] Loaded {len(asteroids)} targets")

# ---------- Output directory ----------
output_dir = os.path.join("results", "real")
os.makedirs(output_dir, exist_ok=True)

# ---------- Plot setup ----------
fig = plt.figure(figsize=(10, 8), facecolor='black')
ax = fig.add_subplot(111, projection='3d', facecolor='black')

ax.scatter(0, 0, 0, color='yellow', s=300, label='Sun')

# ---------- Fetch Data ----------
for name in asteroids:
    try:
        print(f"\nFetching orbit for {name}...")

        # IMPORTANT:
        # If file contains asteroid numbers like: 1, 2, 300
        # Horizons small bodies require "id;" format
        # Extract number from "10 Hygiea"
        number = name.split()[0]
        id_code = number + ";"

        obj = Horizons(
            id=id_code,
            location='@sun',
            epochs={'start': '2025-01-01', 'stop': '2025-12-31', 'step': '5d'}
        )

        vectors = obj.vectors()
        df = vectors.to_pandas()[['datetime_str', 'x', 'y', 'z', 'vx', 'vy', 'vz']]

        filename = os.path.join(output_dir, f"{name}_Real.csv")
        df.to_csv(filename, index=False)

        print(f"Saved: {filename}")

        ax.plot(df['x'], df['y'], df['z'], lw=1)

    except Exception as e:
        print(f"[ERROR] Could not fetch {name}: {e}")

ax.set_xlabel('X [AU]', color='white')
ax.set_ylabel('Y [AU]', color='white')
ax.set_zlabel('Z [AU]', color='white')
ax.tick_params(colors='white')
ax.set_title('Asteroid Orbits (2025) — NASA JPL Horizons', color='white')

ax.view_init(elev=25, azim=45)

plt.show()