import rebound
import json
import numpy as np
import matplotlib.pyplot as plt

# Load asteroid data
with open("data/300_Geraldina.json", 'r') as f:
    data = json.load(f)

el_ast = {e['name']: float(e['value']) for e in data['orbit']['elements']}

# Setup simulation
sim = rebound.Simulation()
sim.units = ('AU', 'day', 'Msun')

# Add Sun
sim.add(m=1.0)  # solar mass

# Real orbital elements for inner planets
planets_data = [
    {'a': 0.3870993, 'e': 0.20564, 'i': 7.0, 'om': 48.3313, 'w': 29.1241, 'ma': 174.7965, 'color': 'lightgray'},
    {'a': 0.723336, 'e': 0.00677, 'i': 3.39471, 'om': 76.68069, 'w': 54.8910, 'ma': 50.1150, 'color': 'violet'},
    {'a': 1.000003, 'e': 0.01671, 'i': 0.00005, 'om': 0.00005, 'w': 102.93735, 'ma': 100.46435, 'color': 'blue'},
    {'a': 1.52371034, 'e': 0.09339, 'i': 1.85061, 'om': 49.57854, 'w': 286.46230, 'ma': 19.41248, 'color': 'brown'}
]

# Add planets to simulation
for p in planets_data:
    sim.add(
        a=p['a'],
        e=p['e'],
        inc=np.radians(p['i']),
        Omega=np.radians(p['om']),
        omega=np.radians(p['w']),
        M=np.radians(p['ma'])
    )

# Add asteroid
sim.add(
    a=el_ast['a'],
    e=el_ast['e'],
    inc=np.radians(el_ast['i']),
    Omega=np.radians(el_ast['om']),
    omega=np.radians(el_ast['w']),
    M=np.radians(el_ast['ma'])
)

sim.move_to_com()

# Integration points
N = 1000
T_ast = el_ast['a']**1.5 * 365.25  # rough orbital period in days (Kepler)
times = np.linspace(0, T_ast, N)

x_all = {p['color']: [] for p in planets_data}
y_all = {p['color']: [] for p in planets_data}
z_all = {p['color']: [] for p in planets_data}
x_ast, y_ast, z_ast = [], [], []

for t in times:
    sim.integrate(t)
    ps = sim.particles
    for i, p in enumerate(planets_data):
        x_all[p['color']].append(ps[i+1].x)
        y_all[p['color']].append(ps[i+1].y)
        z_all[p['color']].append(ps[i+1].z)
    x_ast.append(ps[-1].x)
    y_ast.append(ps[-1].y)
    z_ast.append(ps[-1].z)

# Plotting
fig = plt.figure(figsize=(12,10), facecolor='k')
ax = fig.add_subplot(111, projection='3d', facecolor='k')

# Sun
sun_radius_au = 0.00465
ax.scatter(0,0,0, color='coral', s=sun_radius_au*1e5, label='Sun')

# Planets
for p in planets_data:
    ax.plot(x_all[p['color']], y_all[p['color']], z_all[p['color']],
            color=p['color'], lw=1.5, label=f"Planet {p['color']}")
    ax.scatter(x_all[p['color']][-1], y_all[p['color']][-1], z_all[p['color']][-1],
               color=p['color'], s=50)

# Asteroid
ax.plot(x_ast, y_ast, z_ast, '--', color='red', lw=2, label='Geraldina Orbit')
ax.scatter(x_ast[-1], y_ast[-1], z_ast[-1], color='red', s=100, label='Geraldina')

# Set limits
max_range = max(el_ast['a']*1.2, 1.6)
ax.set_xlim(-max_range, max_range)
ax.set_ylim(-max_range, max_range)
ax.set_zlim(-max_range, max_range)

# Labels
ax.set_xlabel('X [AU]', color='white')
ax.set_ylabel('Y [AU]', color='white')
ax.set_zlabel('Z [AU]', color='white')
ax.tick_params(colors='white')

# Legend
legend = ax.legend(facecolor='k', edgecolor='white')
for text in legend.get_texts():
    text.set_color('white')

# Camera angle
ax.view_init(elev=30, azim=45)

plt.show()
