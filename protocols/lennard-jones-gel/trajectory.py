import readdy
import pandas as pd
from subprocess import check_output, Popen
from shutil import rmtree
from pathlib import Path
import os
import matplotlib.pyplot as plt
import numpy as np
import json

from hydrogels.utils.logger import Logger
logger = Logger('trajectory.py')

def calculate_radius(positions: np.ndarray) -> float:
    logger.debug(type(positions[0][0]))
    logger.debug(f'Calculating radius using:\n{np.round(positions, 4)}')
    covariance_matrix = np.cov(positions)
    logger.debug(f'Covariance Matrix:\n{covariance_matrix}')
    eigenvalues, eigenvectors = np.linalg.eig(np.cov(positions.T))
    radius = np.sqrt(sum([i**2 for i in eigenvalues]))
    logger.debug(f'Calculated gel radius as {radius} using {eigenvalues}')
    return radius

def count(array):
    result = np.histogram(array, range(0, 5))[0]
    return result

def write_json(fname, settings):
    with open(fname, 'r') as f:
        data = json.load(f)
    data['trajectory'] = settings

    with open(fname, 'w') as f:
        json.dump(data, f, indent=2)

def main(**kwargs):
    h5_fname = kwargs['fname']
    logger.info(f'Reading trajectory from {h5_fname}')
    trajectory = readdy.Trajectory(h5_fname)
    trajectory.convert_to_xyz()
    xyz_fname = f'{h5_fname}.xyz'
    n_lines = \
        int(check_output(['wc', '-l' , xyz_fname]).split()[0].decode("utf-8"))

    with open(xyz_fname, 'r') as f:
        n_atoms = int(f.readline().strip())

    start = 2
    n_frames = int(n_lines / (n_atoms + 2))
    f_folder = f'{kwargs.get("traj_folder", "traj")}'
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
        
        if i == 1:
            logger.debug(data)
            gel = data[data['type']=='type_0'].reset_index(drop=True).dropna()[['x', 'y', 'z']]
            gel_radius = calculate_radius(gel.to_numpy(dtype=np.float))
            gel_density = len(gel) / ((4./3.) * np.pi * gel_radius ** 3)

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

    if kwargs.get('json', False):
        write_json(kwargs.get('json'), {
            'N_frames' : n_frames,
            'f_particles' : p_file,
            'f_plot': kwargs.get('plot_file', 'particles.pdf'),
            'f_h5': h5_fname,
            'f_xyz': xyz_fname,
            'f_traj': f_folder,
            'gel_N': max(n_particles.iloc[:, 0]),
            'gel_radius': gel_radius,
            'gel_density': gel_density,
        })

if __name__=='__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--fname', required=True)
    parser.add_argument('--show', action='store_true')
    parser.add_argument('--plot-file', required=False, default='particles.pdf')
    parser.add_argument('--traj-folder', required=False, default='traj')
    parser.add_argument('--particles-file', required=False, default='particles.csv')
    parser.add_argument('--radius-file', required=False, default='radius.csv')
    parser.add_argument('--json', required=False, default=None)
    args = vars(parser.parse_args())
    main(**args)
