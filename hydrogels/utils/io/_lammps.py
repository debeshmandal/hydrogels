import re

import pandas as pd
import numpy as np

from ._core import CoreReader
from ..logger import Logger

from typing import Union

logger = Logger(__name__)

class LAMMPSDataReader(CoreReader):
    def __init__(
        self, 
        fname: str, 
        names: Union[dict, list, tuple] = None, 
        species: dict = None, 
        classes: Union[dict, list, tuple] = None, 
        **kwargs
    ):
        super().__init__()
        self.fname = fname
        if names == None:
            self.names = None
        else:
            self.names = names
        
        self.species = species

        if classes == None:
            self.classes = [None]
        else:
            self.classes = classes
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
        logger.debug(f'reader.names: {self.names}')
        logger.debug(f'mols (from data file): {mols}')
        for idx, i in enumerate(mols):
            logger.debug(f'IDX: {idx} - {i}')
            if isinstance(self.names, dict):
                name = self.names[i]
                try:
                    cls = self.classes[i]
                except IndexError:
                    logger.debug('Caught IndexError whilst allocating classes')
                    cls = None

            elif isinstance(self.names, (list, tuple)):
                name = self.names[idx]
                try:
                    cls = self.classes[idx]
                except IndexError:
                    logger.debug('Caught IndexError whilst allocating classes')
                    cls = None
            else:
                name = i
                cls = None
            mol = atoms[atoms['mol']==i]
            logger.debug(f'{mol}')
            sequence = mol['type'].apply(
                lambda x: self.species[x] if self.species != None else x
            )
            positions = mol[['x', 'y', 'z']]
            
            edges = []
            for j, row in bonds.iterrows():
                if row['atom_1'] in list(mol['id']):
                    edges.append((row['atom_1']-1, row['atom_2']-1))
                elif row['atom_2'] in list(mol['id']):
                    edges.append((row['atom_1']-1, row['atom_2']-1))
            logger.debug(
                f'For mol[{i}], there are {len(positions)} atoms '
                f'and {len(edges)} edges'
            )    
            if len(edges) == 0:
                logger.info(
                    f'Adding {i} as a set of particles because it has no edges'
                )
                self.add_particles(
                    name, 
                    positions.to_numpy()
                )

            else:
                logger.info(
                    f'Adding {i} as a topology because it has edges:'
                    f'\n{pd.DataFrame(edges)}'
                )                    
                self.add_topology(
                    name, 
                    list(sequence), 
                    positions.to_numpy(), 
                    edges, 
                    cls=cls
                )

        return