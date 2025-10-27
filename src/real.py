import os
import matplotlib.pyplot as plt
from astroquery.jplhorizons import Horizons

# Define asteroid targets
asteroids = {
    'Mercury': '199',
    'Venus': '299',
    'Earth': '399',
    'Mars': '499',
    'Jupiter': '599',
    "1_Ceres": "1;",        # Dwarf planet / asteroid
    "2_Pallas": "2;",
    "4_Vesta": "4;",
    "10_Hygiea": "10;",
    "300_Geraldina": "300;"
}
import numpy as np

output_dir = os.path.join("results", "real")
os.makedirs(output_dir, exist_ok=True)

print(" Mean orbital radii from JPL Horizons (in AU):\n")
for name, id_code in asteroids.items():
    obj = Horizons(id=id_code, location='@sun',
                   epochs={'start': '2025-01-01', 'stop': '2025-01-02', 'step': '1d'})
    vectors = obj.vectors()
    df = vectors.to_pandas()[['x', 'y', 'z']]
    r = np.sqrt(df['x']**2 + df['y']**2 + df['z']**2)
    print(f"{name}: {r.mean():.3f} AU")

fig = plt.figure(figsize=(10, 8), facecolor='black')
ax = fig.add_subplot(111, projection='3d', facecolor='black')

# Plot the Sun
ax.scatter(0, 0, 0, color='yellow', s=300, label='Sun')

for name, id_code in asteroids.items():
    print(f"\n🪐 Fetching orbit for {name}...")
    obj = Horizons(id=id_code, location='@sun',
                   epochs={'start': '2025-01-01', 'stop': '2025-12-31', 'step': '5d'})
    vectors = obj.vectors()

    df = vectors.to_pandas()[['datetime_str', 'x', 'y', 'z', 'vx', 'vy', 'vz']]

    filename = os.path.join(output_dir, f"{name}_Real.csv")
    df.to_csv(filename, index=False)
    print(f"Saved: {filename}")

    ax.plot(df['x'], df['y'], df['z'], lw=2, label=name)

ax.set_xlabel('X [AU]', color='white')
ax.set_ylabel('Y [AU]', color='white')
ax.set_zlabel('Z [AU]', color='white')
ax.tick_params(colors='white')
ax.set_title('Asteroid Orbits (2025) — NASA JPL Horizons', color='white')
ax.legend(facecolor='black', edgecolor='white', labelcolor='white')

ax.view_init(elev=25, azim=45)

plt.show()