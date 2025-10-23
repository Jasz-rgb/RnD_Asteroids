import rebound
import json
import numpy as np
import matplotlib.pyplot as plt

with open("targets.txt", "r", encoding="utf-8") as f:
    asteroid_names = [line.strip() for line in f.readlines()[:10]]

sim = rebound.Simulation()
sim.units = ('AU', 'day', 'Msun')
sim.add(m=1.0)

planets_data = [
    {'a': 0.3870993, 'e': 0.20564, 'i': 7.0, 'om': 48.3313, 'w': 29.1241, 'ma': 174.7965, 'color': 'lightgray', 'label': 'Mercury'},
    {'a': 0.723336,  'e': 0.00677, 'i': 3.39471, 'om': 76.68069, 'w': 54.8910, 'ma': 50.1150,  'color': 'violet', 'label': 'Venus'},
    {'a': 1.000003,  'e': 0.01671, 'i': 0.00005, 'om': 0.00005,  'w': 102.93735, 'ma': 100.46435,'color': 'deepskyblue','label': 'Earth'},
    {'a': 1.52371034,'e': 0.09339, 'i': 1.85061, 'om': 49.57854, 'w': 286.46230, 'ma': 19.41248, 'color': 'orangered', 'label': 'Mars'}
]

for p in planets_data:
    sim.add(
        a=p['a'], e=p['e'],
        inc=np.radians(p['i']),
        Omega=np.radians(p['om']),
        omega=np.radians(p['w']),
        M=np.radians(p['ma'])
    )

asteroids = []
for name in asteroid_names:
    file_path = f"data/{name.replace(' ', '_')}.json"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        el = {e['name']: float(e['value']) for e in data['orbit']['elements']}
        sim.add(
            a=el['a'], e=el['e'],
            inc=np.radians(el['i']),
            Omega=np.radians(el['om']),
            omega=np.radians(el['w']),
            M=np.radians(el['ma'])
        )
        asteroids.append({'name': name, 'elements': el})
    except Exception as e:
        print(f"Error loading {name}: {e}")

sim.move_to_com()

N = 1500
T = 365.25 * 4
times = np.linspace(0, T, N)

coords = {p['label']: ([], [], []) for p in planets_data}
asteroid_coords = {a['name']: ([], [], []) for a in asteroids}

for t in times:
    sim.integrate(t)
    ps = sim.particles
    for i, p in enumerate(planets_data):
        coords[p['label']][0].append(ps[i + 1].x)
        coords[p['label']][1].append(ps[i + 1].y)
        coords[p['label']][2].append(ps[i + 1].z)
    for j, a in enumerate(asteroids):
        idx = len(planets_data) + 1 + j
        asteroid_coords[a['name']][0].append(ps[idx].x)
        asteroid_coords[a['name']][1].append(ps[idx].y)
        asteroid_coords[a['name']][2].append(ps[idx].z)

fig = plt.figure(figsize=(12, 10), facecolor='black')
ax = fig.add_subplot(111, projection='3d', facecolor='black')

ax.scatter(0, 0, 0, color='yellow', s=300, label='Sun', edgecolor='gold', linewidths=1.5)

for p in planets_data:
    x, y, z = coords[p['label']]
    ax.plot(x, y, z, color=p['color'], lw=1.5, label=p['label'])
    ax.scatter(x[-1], y[-1], z[-1], color=p['color'], s=30)

for a in asteroids:
    x, y, z = asteroid_coords[a['name']]
    ax.plot(x, y, z, '--', lw=2.2, color='red', label=a['name'])
    ax.scatter(x[-1], y[-1], z[-1], color='red', s=50)

ax.set_xlim(-3, 3)
ax.set_ylim(-3, 3)
ax.set_zlim(-1.5, 1.5)
ax.set_xlabel('X [AU]', color='white')
ax.set_ylabel('Y [AU]', color='white')
ax.set_zlabel('Z [AU]', color='white')
ax.tick_params(colors='white')
ax.grid(False)
ax.set_facecolor('black')
fig.patch.set_facecolor('black')

legend = ax.legend(facecolor='black', edgecolor='white', fontsize=8)
for text in legend.get_texts():
    text.set_color('white')

ax.view_init(elev=25, azim=35)
plt.show()
