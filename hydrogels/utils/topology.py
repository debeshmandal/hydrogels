#!/usr/bin/env python
"""
Objects for handling commonly used high-level readdy topologies
"""
import typing

import numpy as np
import pandas as pd
import readdy

from readdy._internal.readdybinding.api import TopologyRecord
from readdy._internal.readdybinding.common.util import TrajectoryParticle

class TopologyBond:
    """Dataclass containing bond information for a topology"""
    def __init__(self, kind, species_1, species_2, **kwargs):
        self.kind = kind
        self.species = [species_1, species_2]
        self.settings = kwargs

    def register(self, system: "System"):
        if self.kind == 'harmonic':
            system.topologies.configure_harmonic_bond(
                *self.species,
                **self.settings
            )
        else:
            raise TypeError(f'Bond kind must be harmonic but is {self.kind}')
        return

class Topology():
    """
    Wrapper for a readdy topology
    """
    def __init__(self, top_type : str, **kwargs):
        self.top_type = top_type
        self._sequence = kwargs.get('sequence', [])
        self._positions = kwargs.get('positions', np.array([]))
        self._edges = []
        self._bonds = []

    def _string(self):
        return f'{self.top_type}[{self.N}]'

    def __repr__(self):
        return f'Topology<{self._string}>'

    @property
    def N(self):
        return len(self._positions)

    @property
    def positions(self) -> np.ndarray:
        return self._positions

    @positions.setter
    def positions(self, value):
        self._positions = value

    @property
    def sequence(self) -> typing.List[str]:
        return self._sequence

    @sequence.setter
    def sequence(self, value):
        self._sequence = value

    @property
    def edges(self) -> typing.List[tuple]:
        return self._edges

    @edges.setter
    def edges(self, value):
        self._edges = value

    @property
    def bonds(self):
        return self._bonds

    def add_bond(self, *args, **kwargs):
        """Add TopologyBond or args for it"""
        if isinstance(args[0], TopologyBond):
            bond = args[0]
        else:
            bond = TopologyBond(*args, **kwargs)

        self._bonds.append(bond)

    def species(
            self, 
            diffusion_dictionary : dict = None,
            diffusion_constant : float = None
        ) -> dict:
        """
        Returns a dictionary
        """

        if diffusion_dictionary != None and diffusion_constant != None:
            raise ValueError('Please provide only one form for the diffusion constants!')
            

        if diffusion_dictionary:
            assert set(diffusion_dictionary.keys()) == set(self.sequence)
            return diffusion_dictionary

        elif diffusion_constant:
            result = {}
            names = set(self.sequence)
            for name in names:
                result[name] = diffusion_constant
            return result

        raise ValueError('Please provide the diffusion constants, none have been provided!')

    @property
    def is_valid(self) -> bool:
        return len(self.sequence) == len(self.positions)

    def import_dataframe(self, dataframe : pd.DataFrame):
        """
        Parse a dataframe containing information on 
        the sequences and positions of a topology
        and pass this information to the Topology object
        """
        self.sequence = dataframe['sequence']
        self.positions = dataframe.iloc[:, 1:4].values

    @property
    def dataframe(self) -> pd.DataFrame:
        """
        DataFrame form of sequence and positions
        """
        data = {
            'sequence' : self.sequence,
            'x' : self.positions[:, 0],
            'y' : self.positions[:, 1],
            'z' : self.positions[:, 2]
        }
        output = pd.DataFrame(data)
        return output

    def export_xyz(self, fout : str):
        """
        Export to xyz file, readable by OVITO
        """
        self.dataframe.to_csv(fout, index=False, header=False, float_format="%g", sep='\t')

    def add_to_sim(self, simulation: readdy.Simulation, shift: int = 0):
        """
        Adds the topology to a readdy simulation
        """
        topology = simulation.add_topology(
            self.top_type,
            self.sequence,
            self.positions
        )

        for atoms in self.edges:
            topology.get_graph().add_edge(atoms[0] + shift, atoms[1] + shift)

class ReaddyTopology(Topology):
    """
    Class to handle readdy.Topology objects
    """
    def __init__(
        self, 
        topology : TopologyRecord, 
        particles : typing.List[TrajectoryParticle]):
        pass
