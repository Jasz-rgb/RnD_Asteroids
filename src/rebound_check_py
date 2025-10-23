import rebound
import numpy as np
import json
import matplotlib.pyplot as plt

with open("targets.txt", "r", encoding="utf-8") as f:
    first_asteroid = f.readline().strip()

file_path = f"data/{first_asteroid.replace(' ', '_')}.json"
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)
el = {e['name']: float(e['value']) for e in data['orbit']['elements']}

sim = rebound.Simulation()
sim.units = ('AU', 'day', 'Msun')
sim.add(m=1.0)

planets_data = [
    {'a': 0.387, 'e': 0.206, 'i': 7.0, 'om': 48.3, 'w': 29.1, 'ma': 174.8, 'color': 'gray', 'label': 'Mercury'},
    {'a': 1.000, 'e': 0.017, 'i': 0.0, 'om': 0.0, 'w': 102.9, 'ma': 100.5, 'color': 'deepskyblue', 'label': 'Earth'},
    {'a': 1.524, 'e': 0.093, 'i': 1.85, 'om': 49.6, 'w': 286.5, 'ma': 19.4, 'color': 'orangered', 'label': 'Mars'}
]

for p in planets_data:
    sim.add(a=p['a'], e=p['e'], inc=np.radians(p['i']),
            Omega=np.radians(p['om']), omega=np.radians(p['w']),
            M=np.radians(p['ma']))

sim.add(a=el['a'], e=el['e'], inc=np.radians(el['i']),
        Omega=np.radians(el['om']), omega=np.radians(el['w']),
        M=np.radians(el['ma']))

sim.move_to_com()

N = 2000
T = 365.25 * 5
times = np.linspace(0, T, N)

planet_coords = {p['label']: ([], [], []) for p in planets_data}
asteroid_coords = ([], [], [])

for t in times:
    sim.integrate(t)
    ps = sim.particles
    for i, p in enumerate(planets_data):
        planet_coords[p['label']][0].append(ps[i + 1].x)
        planet_coords[p['label']][1].append(ps[i + 1].y)
        planet_coords[p['label']][2].append(ps[i + 1].z)
    asteroid_coords[0].append(ps[len(planets_data) + 1].x)
    asteroid_coords[1].append(ps[len(planets_data) + 1].y)
    asteroid_coords[2].append(ps[len(planets_data) + 1].z)

fig = plt.figure(figsize=(10, 8), facecolor='black')
ax = fig.add_subplot(111, projection='3d', facecolor='black')
ax.scatter(0, 0, 0, color='yellow', s=300, label='Sun', edgecolor='gold')

for p in planets_data:
    x, y, z = planet_coords[p['label']]
    ax.plot(x, y, z, color=p['color'], lw=1.5, label=p['label'])
    ax.scatter(x[-1], y[-1], z[-1], color=p['color'], s=30)

x_a, y_a, z_a = asteroid_coords
ax.plot(x_a, y_a, z_a, '--', lw=2.2, color='red', label=first_asteroid)
ax.scatter(x_a[-1], y_a[-1], z_a[-1], color='red', s=50)

ax.set_xlim(-3, 3)
ax.set_ylim(-3, 3)
ax.set_zlim(-1.5, 1.5)
ax.set_xlabel('X [AU]', color='white')
ax.set_ylabel('Y [AU]', color='white')
ax.set_zlabel('Z [AU]', color='white')
ax.tick_params(colors='white')
ax.set_facecolor('black')
fig.patch.set_facecolor('black')

legend = ax.legend(facecolor='black', edgecolor='white', fontsize=8)
for text in legend.get_texts():
    text.set_color('white')

ax.view_init(elev=25, azim=35)
plt.title(f"3D Orbit of {first_asteroid}", color='white')
plt.show()
