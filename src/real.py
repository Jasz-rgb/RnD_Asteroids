"""Fetch real asteroid data from JPL Horizons (100 asteroids, 20 years, 5-day step)"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import numpy as np
import matplotlib.pyplot as plt
from astroquery.jplhorizons import Horizons

# ---------- Read targets ----------
targets_file = r"C:/Users/JASMINE/Desktop/RnD_asteroid/targets_english.txt"

asteroids = []

with open(targets_file, "r", encoding="utf-8") as f:
    for line in f:
        name = line.strip()
        if name:
            asteroids.append(name)

# ✅ LIMIT TO FIRST 100 ASTEROIDS
asteroids = asteroids[:100]

print(f"[INFO] Using {len(asteroids)} asteroids (first 100)")

# ---------- Output directory ----------
output_dir = os.path.join("results", "real")
os.makedirs(output_dir, exist_ok=True)

# ---------- Plot setup ----------
fig = plt.figure(figsize=(10, 8), facecolor='black')
ax = fig.add_subplot(111, projection='3d', facecolor='black')

ax.scatter(0, 0, 0, color='yellow', s=300, label='Sun')

# ---------- 20 YEAR RANGE ----------
START_DATE = '2025-01-01'
END_DATE   = '2045-01-01'
STEP       = '5d'

# ---------- Fetch Data ----------
for name in asteroids:
    try:
        print(f"\nFetching orbit for {name} (20 years)...")

        number = name.split()[0]
        id_code = number + ";"

        obj = Horizons(
            id=id_code,
            location='@sun',
            epochs={
                'start': START_DATE,
                'stop': END_DATE,
                'step': STEP
            }
        )

        vectors = obj.vectors()

        df = vectors.to_pandas()[[
            'datetime_str', 'x', 'y', 'z', 'vx', 'vy', 'vz'
        ]]

        safe_name = name.replace(" ", "_")
        filename = os.path.join(output_dir, f"{safe_name}_Real.csv")
        df.to_csv(filename, index=False)

        print(f"Saved: {filename}")

        # Plot trajectory
        ax.plot(df['x'], df['y'], df['z'], lw=0.8)

    except Exception as e:
        print(f"[ERROR] Could not fetch {name}: {e}")

# ---------- Plot Styling ----------
ax.set_xlabel('X [AU]', color='white')
ax.set_ylabel('Y [AU]', color='white')
ax.set_zlabel('Z [AU]', color='white')
ax.tick_params(colors='white')
ax.set_title('Asteroid Orbits (2005–2025) — NASA JPL Horizons', color='white')

ax.view_init(elev=25, azim=45)

plt.show()

print("\n✅ 20-year real ephemeris data generation complete.")