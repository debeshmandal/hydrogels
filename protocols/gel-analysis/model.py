import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.spatial

from softnanotools.logger import Logger
logger = Logger('MODEL')

def read_lammps_conf(fname):
    data = {}
    with open(fname, 'r') as f:

        # skip first two lines
        f.readline()
        f.readline()

        # read atom + bond types
        logger.debug(f'Setting...')
        for i in range(4):
            line = f.readline().split()
            value = line[0]
            label = '_'.join(line[1:])
            logger.debug(f'    {label}{" " * (10 - len(label))}\t-> {value}')
            data[label] = int(value)

        for i, line in enumerate(f.readlines()):
            if re.findall('Atoms', line):
                atoms_line = i+6
                logger.debug(f'Line that atoms start on: {atoms_line}')

            elif re.findall('Bonds', line):
                bonds_line = i+6
                logger.debug(f'Line that bonds start on: {bonds_line}')

    data['particles'] = pd.read_csv(
        fname, 
        skiprows=atoms_line+2,
        header=None,
        delim_whitespace=True,
        nrows=data['atoms']
    ).rename(columns={
        0: 'id',
        1: 'mol',
        2: 'type',
        3: 'x',
        4: 'y',
        5: 'z',
    })[['id', 'mol', 'type', 'x', 'y', 'z']].sort_values(
        by='id'
    ).reset_index(
        drop=True
    )

    logger.debug(f'Particles:\n{data["particles"]}')
    
    data['edges'] = pd.read_csv(
        fname, 
        skiprows=bonds_line+1,
        header=None,
        delim_whitespace=True,
        nrows=data['bonds']
    ).rename(columns={
        0: 'id',
        1: 'type',
        2: 'atom_1',
        3: 'atom_2'
    }).sort_values(by='id').reset_index(drop=True)

    logger.debug(f'Edges:\n{data["edges"]}')

    return data

class _Model:
    def __init__(self, particles, edges):
        self.particles = particles
        self.edges = edges
    
    @property
    def N(self):
        return len(self.particles)

    @property
    def X(self):
        return len(self.crosslinkers)
    
    @property
    def E(self):
        return len(self.edges)

    @property
    def crosslinkers(self):
        return self.particles[self.particles['type']==2].copy()

    def positions(self, crosslinkers=False):
        if crosslinkers:
            particles = self.crosslinkers.copy()
        else:
            particles = self.particles.copy()

        return particles[['x', 'y', 'z']].to_numpy()
        
    def rdf(self, crosslinkers=False, bins=50):
        distances = sorted(
            scipy.spatial.distance.pdist(
                self.positions(
                    crosslinkers=crosslinkers
                )
            )
        )
        rdf = np.histogram(distances, bins=bins)
        return rdf

    def gyration(self):
        points = self.positions()
        center = points.mean(0)
        # normalized points
        normed_points = points - center[None,:]
        tensor = np.einsum('im,in->mn', normed_points,normed_points)/len(points)
        return (
            tensor[0, 0], 
            tensor[1, 1], 
            tensor[2, 2], 
            tensor[0, 1], 
            tensor[0, 2], 
            tensor[1, 2]
        )

    def bond_to_atoms_ratio(self):
        return self.E / self.N
    
    def plot_rdf(self, show=False, target=None, title=None, **kwargs):

        fig, ax = plt.subplots()

        # N
        rdf = self.rdf(**kwargs)
        delta = np.diff(rdf[0])
        logger.debug(
            pd.DataFrame({                
                'distance': rdf[1][:-1],
                'count': rdf[0], 
                'delta': [0] + list(delta)
            })
        )
        ax.plot(rdf[1][:-1], rdf[0]/sum(rdf[0]), label=f'N={sum(rdf[0])}')

        # X
        rdf = self.rdf(bins=rdf[1], crosslinkers=True)
        delta = np.diff(rdf[0])
        logger.debug(
            pd.DataFrame({                
                'distance': rdf[1][:-1],
                'count': rdf[0], 
                'delta': [0] + list(delta)
            })
        )
        ax.plot(rdf[1][:-1], rdf[0]/sum(rdf[0]), label=f'X={sum(rdf[0])}')
                
        if title:
            ax.set_title(title)
        ax.set_xlabel('r')
        ax.set_ylabel('g(r)')

        ax.legend()

        if target:
            plt.savefig(target)

        if show:
            plt.show()

    def mesh_size(self):
        return

class Model(_Model):
    def __init__(self, fname):
        self.fname = fname
        data = read_lammps_conf(self.fname)
        super().__init__(
            data['particles'], 
            data['edges']
        )

    def __repr__(self):
        return f"[{self.fname}]({self.N}/{self.X} E={self.E})"

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--fname', default='lammps.test.conf')
    model = Model(parser.parse_args().fname)
    logger.info(f"{model}\n")
    logger.info(f"    Bonds:Atoms     -> {model.bond_to_atoms_ratio()}")
    logger.info(f"    Gyration Tensor -> {' '.join([f'{i:.3f}' for i in model.gyration()])}")
    model.plot_rdf(show=True, bins=100, title=model.fname.split('/')[-1])
    #logger.info(f"    Mesh Size     -> {model.mesh_size()}")
