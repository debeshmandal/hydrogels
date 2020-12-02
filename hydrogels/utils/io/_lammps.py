import re

import pandas as pd
import numpy as np

from ._core import CoreReader
from ..logger import Logger

from typing import Union

logger = Logger(__name__)

class LAMMPSDataReader(CoreReader):
    def __init__(self, fname, names: Union[dict, list, tuple] = None, species: dict = None, **kwargs):
        super().__init__()
        self.fname = fname
        self.names = names
        self.species = species
        self._read()
        

    def _read(self):
        """Reads a LAMMPS Data File containing configuration and 
        topology information"""

        box = {}

        with open(self.fname, 'r') as f:
            for i, line in enumerate(f.readlines()):
                if re.findall("atoms", line):
                    n_atoms = int(line.split()[0])
                elif re.findall("bonds", line):
                    n_bonds = int(line.split()[0])
                elif re.findall("xlo xhi", line):
                    box['x'] = [float(j) for j in line.split()[:2]]
                elif re.findall("ylo yhi", line):
                    box['y'] = [float(j) for j in line.split()[:2]]
                elif re.findall("zlo zhi", line):
                    box['z'] = [float(j) for j in line.split()[:2]]
                elif re.findall("Atoms", line):
                    skip_atoms = i + 1
                elif re.findall("Bonds", line):
                    skip_bonds = i + 1
                    break

        self.metadata['box'] = np.array([
            ([float(i) for i in box['x']][1] - [float(i) for i in box['x']][0]),
            ([float(i) for i in box['y']][1] - [float(i) for i in box['y']][0]),
            ([float(i) for i in box['z']][1] - [float(i) for i in box['z']][0]),
        ])

        logger.debug(f'Box: {self.metadata["box"]}')

        atoms = pd.read_csv(
            self.fname,
            delim_whitespace=True,
            header=None,
            nrows=n_atoms,
            skiprows=skip_atoms,
        ).rename(columns={
            0: 'id',
            1: 'mol',
            2: 'type',
            3: 'x',
            4: 'y',
            5: 'z',
        })

        logger.debug(f'ATOMS:\n{atoms}')
        
        bonds = pd.read_csv(
            self.fname,
            delim_whitespace=True,
            header=None,
            nrows=n_bonds,
            skiprows=skip_bonds,
        ).rename(columns={
            0: 'id',
            1: 'type',
            2: 'atom_1',
            3: 'atom_2',
        })

        logger.debug(f'BONDS:\n{bonds}')

        mols = set(list(atoms['mol']))
        for idx, i in enumerate(mols):
            if isinstance(self.names, dict):
                name = self.names[i]
            elif isinstance(self.names, (list, tuple)):
                name = self.names[idx]
            else:
                name = i
            mol = atoms[atoms['mol']==i]
            sequence = mol['type'].apply(
                lambda x: self.species[x] if self.species != None else x
            )
            positions = mol[['x', 'y', 'z']]
            edges = []
            for j, row in bonds.iterrows():
                if row['atom_1'] in mol['id']:
                    edges.append((row['atom_1']-1, row['atom_2']-1))
                elif row['atom_2'] in mol['id']:
                    edges.append((row['atom_1']-1, row['atom_2']-1))
                
            if len(edges) == 0:
                self.add_particles(name, positions.to_numpy())

            else:
                self.add_topology(name, list(sequence), positions.to_numpy(), edges)

        return