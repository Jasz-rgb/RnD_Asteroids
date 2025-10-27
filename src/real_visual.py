import matplotlib.pyplot as plt
from astroquery.jplhorizons import Horizons

ids = {
    'Mercury': '199',
    'Venus': '299',
    'Earth': '399',
    'Mars': '499',
    'Jupiter': '599',
    'Ceres': 'Ceres'  # Ceres ID
}

fig = plt.figure(figsize=(10, 8), facecolor='k')
ax = fig.add_subplot(111, projection='3d', facecolor='k')

ax.scatter(0, 0, 0, color='yellow', s=300, label='Sun')

for name, body_id in ids.items():
    obj = Horizons(id=body_id, location='@sun', epochs={'start': '2025-01-01', 'stop': '2025-12-31', 'step': '5d'})
    vectors = obj.vectors()
    df = vectors.to_pandas()[['datetime_str', 'x', 'y', 'z']]
    
    if name == 'Ceres':
        ax.plot(df['x'], df['y'], df['z'], color='red', lw=2, linestyle='--', label='Ceres (Dwarf Planet)')
    else:
        ax.plot(df['x'], df['y'], df['z'], lw=2, label=name)

ax.set_xlabel('X [AU]', color='white')
ax.set_ylabel('Y [AU]', color='white')
ax.set_zlabel('Z [AU]', color='white')
ax.tick_params(colors='white')
ax.set_title('Solar System Orbits (2025)', color='white')

ax.legend(facecolor='k', edgecolor='white', labelcolor='white')

ax.view_init(elev=25, azim=45)
plt.show()
