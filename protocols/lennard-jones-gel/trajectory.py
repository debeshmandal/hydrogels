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

def main(**kwargs):
    h5_fname = kwargs['fname']
    trajectory = readdy.Trajectory(h5_fname)
    trajectory.convert_to_xyz()
    xyz_fname = f'{h5_fname}.xyz'
    n_lines = \
        int(check_output(['wc', '-l' , xyz_fname]).split()[0].decode("utf-8"))

    with open(xyz_fname, 'r') as f:
        n_atoms = int(f.readline().strip())

    start = 2
    n_frames = int(n_lines / (n_atoms + 2))
    f_folder = f'./{kwargs.get("traj_folder", "traj")}'
    try:
        rmtree(Path(f_folder))
    except FileNotFoundError:
        pass

    Path.mkdir(Path(f_folder))

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
        with open(f'{f_folder}/readdy.xyz.{i}', 'w') as f:
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
    fig.savefig(kwargs.get('plot_file', 'particles.pdf'))
    p_file = kwargs.get('particles_file', None)
    if p_file:
        n_particles.to_csv(p_file, index=None)
    if kwargs.get('show', False):
        plt.show()

if __name__=='__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('fname')
    parser.add_argument('--show', action='store_true')
    parser.add_argument('--plot-file', required=False, default='particles.pdf')
    parser.add_argument('--traj-folder', required=False, default='traj')
    parser.add_argument('--particles-file', required=False, default=None)
    args = vars(parser.parse_args())
    main(**args)
