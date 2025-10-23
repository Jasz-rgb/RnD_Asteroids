import rebound
import json
import numpy as np
import matplotlib.pyplot as plt
from astroquery.jplhorizons import Horizons
import pandas as pd

# Fetch real orbital data from NASA Horizons
obj = Horizons(id='300', location='@sun', epochs={'start':'2025-01-01', 'stop':'2025-12-31', 'step':'5d'})
vectors = obj.vectors()
df = vectors.to_pandas()[['datetime_str', 'x', 'y', 'z']]

# Run Rebound simulation
sim = rebound.Simulation()
sim.units = ('AU', 'day', 'Msun')
sim.add(m=1.0)

with open("data/300_Geraldina.json", "r", encoding="utf-8") as f:
    data = json.load(f)
el = {e['name']: float(e['value']) for e in data['orbit']['elements']}
sim.add(a=el['a'], e=el['e'], inc=np.radians(el['i']),
        Omega=np.radians(el['om']), omega=np.radians(el['w']), M=np.radians(el['ma']))
sim.move_to_com()

N = len(df)
times = np.linspace(0, 365, N)
x_sim, y_sim, z_sim = [], [], []

for t in times:
    sim.integrate(t)
    ps = sim.particles
    x_sim.append(ps[1].x)
    y_sim.append(ps[1].y)
    z_sim.append(ps[1].z)

# Plot both orbits
fig = plt.figure(figsize=(10, 8), facecolor='k')
ax = fig.add_subplot(111, projection='3d', facecolor='k')

ax.scatter(0, 0, 0, color='yellow', s=300, label='Sun')
ax.plot(df['x'], df['y'], df['z'], color='lime', lw=2, label='NASA Horizons (Real)')
ax.plot(x_sim, y_sim, z_sim, '--', color='red', lw=2, label='Rebound Simulation')

ax.set_xlabel('X [AU]', color='white')
ax.set_ylabel('Y [AU]', color='white')
ax.set_zlabel('Z [AU]', color='white')
ax.tick_params(colors='white')
ax.legend(facecolor='k', edgecolor='white', labelcolor='white')

ax.set_title('Asteroid 300 Geraldina: Real vs Simulated Orbit', color='white')
ax.view_init(elev=25, azim=45)
plt.show()
