import numpy as np
import pandas as pd
import json
import yaml
from typing import Tuple, List
from pathlib import Path
import subprocess
from collections import Counter

from hydrogels.utils.logger import Logger
logger = Logger('CONVERT')

def update_edges(edges: pd.DataFrame, particles: pd.DataFrame) -> pd.DataFrame:

    edges['x1'] = edges['atom_1'].apply(lambda x: particles['x'][x-1])
    edges['y1'] = edges['atom_1'].apply(lambda x: particles['y'][x-1])
    edges['z1'] = edges['atom_1'].apply(lambda x: particles['z'][x-1])
    edges['x2'] = edges['atom_2'].apply(lambda x: particles['x'][x-1])
    edges['y2'] = edges['atom_2'].apply(lambda x: particles['y'][x-1])
    edges['z2'] = edges['atom_2'].apply(lambda x: particles['z'][x-1])

    edges['dx'] = edges['x2'] - edges['x1']
    edges['dy'] = edges['y2'] - edges['y1']
    edges['dz'] = edges['z2'] - edges['z1']

    edges['length'] = np.sqrt(sum([
        edges['dx'] ** 2,
        edges['dy'] ** 2,
        edges['dz'] ** 2,
    ]))
    return edges

def find_crosslinkers(particles: pd.DataFrame, edges: pd.DataFrame):
    particles['crosslinker'] = len(particles) * [False]
    for i in [item for item, count in Counter(
        edges[['atom_1', 'atom_2']].to_numpy().flatten()
    ).items() if count > 3]:
        particles.at[i, 'crosslinker'] = True
    return particles, edges

def read_oxDNA_bonds(fname: str):
    logger.info(f'Reading {fname} bonds files')
    edges = []
    with open(fname, 'r') as f:
        N, crosslinkers = [int(i) for i in f.readline().split()[2:4]]
        logger.debug(f'N: {N}, X: {crosslinkers}')
        box = [float(i) for i in f.readline().split()][:3]
        logger.debug(f'BOX: {box}')
        for i in range(N):
            _ = f.readline()
        for i in range(N):
            line = f.readline().split()
            idx, bonds = [int(i) for i in line]
            for j in f.readline().split():
                edges.append(tuple(sorted((idx, int(j)))))
    edges = tuple(set(tuple(edges)))
    particles = pd.read_csv(fname, skiprows=2, nrows=N, delim_whitespace=True, header=None)
    particles, edges = format_dataframes(particles, edges, box)

    #edges = edges.sort_values(by=['atom_1', 'atom_2']).reset_index(drop=True)
    if any(edges['length'] > box[0] / 2):
        logger.warning(f'Some edges are longer than {box[0] / 2}:\n{edges[edges["length"] > (box[0] / 2)]}')
    logger.debug(f'Particles:\n{particles}')
    logger.debug(f'Edges:\n{edges}')
    logger.info(
        f'Finished Converting!\n'
        f'  Particles:\t {len(particles)}\n'
        f'  \tNormal:\t {len(particles[~particles["crosslinker"]])}\n'
        f'  \tCross:\t {len(particles[particles["crosslinker"]])}\n'
        f'  Edges:\t({len(edges)})'
    )
    return particles, edges, box

def format_dataframes(
    _particles: pd.DataFrame,
    _edges: pd.DataFrame,
    box: List[float]
):  
    particles = _particles.rename(columns={
        0: 'x',
        1: 'y',
        2: 'z',
    })

    for e, i in enumerate(['x', 'y', 'z']):
        temp = particles[abs(particles[i]) < (box[e] / 2)]
        particles[i] -= temp.mean()[i]
        particles[i] = particles[i].apply(lambda x: (x - box[e]) if (x > (box[e])) else x)
        particles[i] = particles[i].apply(lambda x: (x + box[e]) if (x < (-box[e])) else x)

    particles['bild-cmd'] = ['.sphere'] * len(particles)
    particles['r'] = [0.4] * len(particles)

    logger.debug(f'Formatted Particles:\n{particles}')

    edges = pd.DataFrame(_edges).rename(columns={
        0: 'atom_1',
        1: 'atom_2'
    })
    edges['bild-cmd'] = ['.v'] * len(edges)
    logger.debug(f'Edges (no positions):\n{edges}')
    edges = update_edges(edges, particles)
    logger.debug(f'Formatted Edges:\n{edges}')

    if any(edges['length'] > box[0] / 2):
        logger.warning(f'Some edges are longer than {box[0] / 2}:\n{edges[edges["length"] > (box[0] / 2)]}')

    particles, edges = find_crosslinkers(particles, edges)

    return particles, edges

def main():
    return

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('N', type=int)
    parser.add_argument('-s', '--setup-yaml', required=True, type=str)
    parser.add_argument('--xyz', action='store_true')
    parser.add_argument('--bild', action='store_true')
    parser.add_argument('--ovito', action='store_true')
    main(**vars(parser.parse_args()))