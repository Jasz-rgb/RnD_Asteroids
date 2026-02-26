"""file to get the rebound library data for all the asteroids"""
import os
import json
import numpy as np
import pandas as pd
import rebound
from datetime import datetime, timedelta

# -------------------- Output directory --------------------
output_dir = os.path.join("results", "rebound")
os.makedirs(output_dir, exist_ok=True)

# -------------------- Planet orbital elements --------------------
planets = {
    'Mercury': {'a': 0.387, 'e': 0.206, 'i': 7.0, 'om': 48.3, 'w': 29.1, 'ma': 174.8},
    'Venus':   {'a': 0.723, 'e': 0.007, 'i': 3.4, 'om': 76.7, 'w': 54.9, 'ma': 50.1},
    'Earth':   {'a': 1.000, 'e': 0.017, 'i': 0.0, 'om': 0.0,  'w': 102.9, 'ma': 100.5},
    'Mars':    {'a': 1.524, 'e': 0.093, 'i': 1.85,'om': 49.6, 'w': 286.5,'ma': 19.4},
    'Jupiter': {'a': 5.204, 'e': 0.049, 'i': 1.3, 'om': 100.6,'w': 273.9,'ma': 20.0}
}

# -------------------- Read asteroid targets --------------------
targets_file = r"C:/Users/JASMINE/Desktop/RnD_asteroid/targets_english.txt"

asteroids = []
with open(targets_file, "r", encoding="utf-8") as f:
    for line in f:
        name = line.strip()
        if name:
            name = name.replace(" ", "_")
            asteroids.append(name)

print(f"[INFO] Loaded {len(asteroids)} asteroid targets")

# -------------------- Time setup --------------------
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 12, 31)
delta_days = 5
times = np.arange(0, (end_date - start_date).days + delta_days, delta_days)

# -------------------- Simulation Function --------------------
def simulate_and_save(name, a, e, i, om, w, ma):
    sim = rebound.Simulation()
    sim.units = ('AU', 'day', 'Msun')
    sim.add(m=1.0)  # Sun
    sim.add(
        a=a,
        e=e,
        inc=np.radians(i),
        Omega=np.radians(om),
        omega=np.radians(w),
        M=np.radians(ma)
    )
    sim.move_to_com()

    data = []

    for t in times:
        sim.integrate(t)
        p = sim.particles[1]
        current_date = start_date + timedelta(days=int(t))
        datetime_str = current_date.strftime("A.D. %Y-%b-%d 00:00:00.0000")

        r = np.sqrt(p.x**2 + p.y**2 + p.z**2)

        data.append([
            datetime_str,
            p.x, p.y, p.z,
            p.vx, p.vy, p.vz,
            r
        ])

    df = pd.DataFrame(
        data,
        columns=["datetime_str", "x", "y", "z", "vx", "vy", "vz", "r_AU"]
    )

    mean_r = df["r_AU"].mean()

    csv_path = os.path.join(output_dir, f"{name}_Rebound.csv")
    df.to_csv(csv_path, index=False)

    print(f"{name:<25} — Saved | Mean radius: {mean_r:.3f} AU")

    return mean_r

# -------------------- Run Planet Simulations --------------------
mean_radii = {}

for name, el in planets.items():
    mean_radii[name] = simulate_and_save(name, **el)

# -------------------- Run Asteroid Simulations --------------------
for asteroid in asteroids:

    file_path = os.path.join("data", f"{asteroid}.json")

    if not os.path.exists(file_path):
        print(f"[WARNING] Skipping {asteroid}: JSON file not found.")
        continue

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Extract orbital elements
        el = {e['name']: float(e['value']) for e in data['orbit']['elements']}

        mean_radii[asteroid] = simulate_and_save(
            asteroid,
            a=el['a'],
            e=el['e'],
            i=el['i'],
            om=el['om'],
            w=el['w'],
            ma=el['ma']
        )

    except Exception as e:
        print(f"[ERROR] Failed to simulate {asteroid}: {e}")

# -------------------- Print Summary --------------------
print("\nMean orbital radii (Rebound simulation):\n")
for name, r in mean_radii.items():
    print(f"{name:<25}: {r:.3f} AU")

print("\nAll results saved to results/rebound/")