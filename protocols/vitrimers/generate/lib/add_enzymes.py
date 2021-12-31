#!/usr/bin/env python
"""Reads a LAMMPS Configuration File and adds N enzymes in
random positions within the box"""

import json
import re 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform

from softnanotools.logger import Logger
logger = Logger('ADD ENZYMES')

def read_conf(fname: str) -> dict:
    settings = {}
    with open(fname, 'r') as f:
        for i, line in enumerate(f.readlines()):
            if line.endswith('atoms\n'):
                logger.debug(f'Found atoms at line at {i}: {line}')
                settings['atoms'] = int(line.split()[0])

            if line.endswith('atom types\n'):
                logger.debug(f'Found atom types at line at {i}: {line}')
                settings['atom_types'] = int(line.split()[0])

            if line.endswith('xlo xhi\n'):
                logger.debug(f'Found box at line at {i}: {line}')
                settings['box'] = float(line.split()[1])

            if re.findall('Atoms', line):
                logger.debug(f'Found Atoms line at {i}')
                settings['atoms_line'] = i+1

    assert set(settings.keys()) == {'box', 'atom_types', 'atoms_line', 'atoms'}


    atoms = pd.read_csv(
        fname, 
        delim_whitespace=True, 
        skiprows=settings['atoms_line']+1,
        nrows=settings['atoms'],
        header=None
    )

    logger.debug(atoms)

    radius = np.mean([
        atoms[3].max() - atoms[3].min(),
        atoms[4].max() - atoms[4].min(),
        atoms[5].max() - atoms[5].min(),
    ])

    logger.debug(f'Radius is {radius}')

    settings['radius'] = radius
    
    # calculate radius

    logger.debug(json.dumps(settings, indent=2))
            
    return settings

def generate_enzyme_positions(box: float, radius: float, **kwargs) -> np.ndarray:
    # get number
    N = kwargs['N']
    
    # scale box down to avoid enzymes escaping it
    # box = 0.85 * box
    assert box > radius

    logger.info(f'Generating enzymes from r={radius:.3f} to r={box:.3f}')

    # get volume bounds
    V_min = (4./3. * np.pi * radius ** 3)
    V_max = (4./3. * np.pi * box ** 3)

    # print volume bounds

    logger.debug(f'Bounds for Volume = [{V_min:.2f}, {V_max:.2f}]')
    logger.debug(f'Yielding [{V_min/V_max:.2f}, 1.0]')

    # get uniform distribution of volume, azimuthal and cos(elevation)
    V = np.random.uniform(V_min/V_max, 1.0, N)
    phi = np.random.uniform(0, 2 * np.pi, N)
    costheta = np.random.uniform(-1., 1., N)

    # get elevation and radius
    theta = np.arccos(costheta)
    r = box * V ** (1./3.)

    # convert to cartesian coordinates
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)

    # stack into single array
    array = np.vstack([x, y, z]).T

    # print to debug
    logger.debug(array)

    # check for overlaps
    distances = pdist(array)
    limit = 0.8
    histogram = np.histogram(np.linalg.norm(array, axis=1))
    logger.debug('\nHistogram of distances from centre:')
    logger.debug('   '.join([f'{i:.2f}' for i in histogram[1][:-1]]))
    logger.debug('    '.join([f'{i:4d}' for i in histogram[0]]))
    try:
        assert any(distances < limit) == False
    except AssertionError:
        logger.error(
            f'Some distances were shorter than {limit}:\n{distances[distances < limit]}'
        )

    return array

def update_file(fname: str, positions: np.ndarray, out: str, **settings):
    with open(fname, 'r') as f:
        lines = f.readlines()

    with open(out, 'w') as f:
        for i, line in enumerate(lines):
            if line.endswith('atoms\n'):
                f.write(f'{settings["atoms"]} atoms\n')
                continue
            if line.endswith('atom types\n'):
                f.write(f'{settings["atom_types"]} atom types\n')
                continue
            if i == 15:
                f.write(line)
                f.write(f'{settings["atom_types"]} 1.0\n')
                continue

            if line.endswith('xlo xhi\n'):
                if settings.get('box', None):
                    f.write(f'{-settings["box"]:.3f} {settings["box"]:.3f} xlo xhi\n')
                    continue

            if line.endswith('ylo yhi\n'):
                if settings.get('box', None):
                    f.write(f'{-settings["box"]:.3f} {settings["box"]:.3f} ylo yhi\n')
                    continue

            if line.endswith('zlo zhi\n'):
                if settings.get('box', None):
                    f.write(f'{-settings["box"]:.3f} {settings["box"]:.3f} zlo zhi\n')
                    continue


            if i == settings["atoms_line"] + settings["atoms"] - settings['N']:
                f.write(line)
                for j, pos in enumerate(positions):
                    f.write(f'{j + settings["atoms"] - settings["N"] + 1} 2 {settings["atom_types"]} {pos[0]:.8e} {pos[1]:.8e} {pos[2]:.8e} 0 0 0\n')
                continue

            # this would be for velocities
            #if i == settings["atoms_line"] + 3 + 2 * (settings["atoms"] - settings['N']):
            #    f.write(line)
            #    for j, pos in enumerate(positions):
            #        f.write(f'{j + settings["atoms"] - settings["N"] + 1} 0.0 0.0 0.0\n')
            #    continue
                
            else:
                f.write(line)
    return

def main(number: int, fname: str, out: str, box: float):

    logger.info(f'Adding {number} enzymes to {fname}->{out}')

    # get settings
    settings = read_conf(fname)

    # update settings
    settings['N'] = number
    settings['atom_types'] += 1
    settings['atoms'] += number

    if box:
        settings['box'] = box

    # get positions of new atoms
    positions = generate_enzyme_positions(**settings)

    # write new file updated with enzymes
    update_file(fname, positions, out, **settings)

    return

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('number', type=int)
    parser.add_argument('-f', '--fname', default='lammps.test.conf')
    parser.add_argument('-o', '--out', default='lammps.main.conf')
    parser.add_argument('-b', '--box', default=None, type=float)
    main(
        **vars(parser.parse_args())
    )
