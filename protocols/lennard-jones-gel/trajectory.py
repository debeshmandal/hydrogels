import readdy
import pandas as pd
from subprocess import check_output, Popen
from shutil import rmtree
from pathlib import Path
import os
import matplotlib.pyplot as plt
import numpy as np

def count(array):
    result = np.histogram(array, range(0, 5))[0]
    return result

h5_fname = '_out.h5'
trajectory = readdy.Trajectory(h5_fname)
trajectory.convert_to_xyz()
xyz_fname = f'{h5_fname}.xyz'
n_lines = \
    int(check_output(['wc', '-l' , xyz_fname]).split()[0].decode("utf-8"))

with open(xyz_fname, 'r') as f:
    n_atoms = int(f.readline().strip())

start = 2
n_frames = int(n_lines / (n_atoms + 2))
f_folder = './traj'
try:
    rmtree(Path('./traj'))
except FileNotFoundError:
    pass

Path.mkdir(Path('./traj'))

particles = trajectory.read_observable_particles()
timesteps = particles[0]
particle_types = particles[1]
n_particles = pd.DataFrame()

for i in range(n_frames - 1):
    data = pd.read_csv(
        xyz_fname, 
        delimiter='\t', 
        skiprows=start + i*(n_atoms + 2), 
        nrows=n_atoms, 
        header=None,
        na_values='0'
    ).rename(columns={
        0: 'type',
        1: 'x',
        2: 'y',
        3: 'z'
    })
    n_active_atoms = n_atoms - data.isnull().sum().values[-1]
    data = data.dropna().reset_index(drop=True)
    with open(f'./traj/traj.xyz.{i}', 'w') as f:
        f.write(f'{n_active_atoms}\n\n')
        data.to_csv(f, index=False, header=False, float_format="%g", sep='\t')
    n_particles = pd.concat([n_particles, pd.DataFrame(count(particle_types[i])).T])

n_particles = n_particles.reset_index(drop=True)
fig, ax = plt.subplots()
particle_names = [
    'gel',
    'unbonded',
    'released',
    'enzyme',
]
for i in range(4):
    ax.plot(n_particles[i], label=particle_names[i])
ax.set_xlabel('Timestep')
ax.set_ylabel('Number of Particles')
ax.legend(frameon=False)
fig.savefig('particles.pdf')
plt.show()
