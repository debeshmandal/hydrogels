import re

import pandas as pd
import numpy as np

from ._core import CoreReader

class LAMMPSDataReader(CoreReader):
    def __init__(self, fname):
        self.fname = fname
        super().__init__(*self._read())

    def _read(self):
        particles = {}
        topologies = []
        metadata = {}

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

        atoms = pd.read_csv(
            self.fname,
            delim_whitespace=True,
            header=None,
            nrows=n_atoms,
            skiprows=skip_atoms,
        )
        
        bonds = pd.read_csv(
            self.fname,
            delim_whitespace=True,
            header=None,
            nrows=n_bonds,
            skiprows=skip_bonds,
        )

        return particles, topologies, metadata