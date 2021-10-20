#!/usr/bin/env python
"""
Objects for handling commonly used high-level readdy topologies
"""
import typing

import numpy as np
import pandas as pd
import networkx as nx

import readdy

from softnanotools.logger import Logger
logger = Logger(__name__)

from readdy._internal.readdybinding.api import TopologyRecord #type: ignore
from readdy._internal.readdybinding.common.util import TrajectoryParticle #type:ignore

class System: pass # placeholder for System class

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

    Parameters:
        sequence:
            String or list containing sequence of particles
        names:
            Names of any topology species that aren't contained in sequence
        positions:
            Positions of particles, should correspond to sequence
        edges:
            Connectivity of sequence in terms of bonding
        bonds:
            List of TopologyBond instances containing bonding information
    """
    def __init__(self, top_type : str, **kwargs):
        self.top_type = top_type
        _sequence = kwargs.get('sequence', [])
        if isinstance(_sequence, str):
            _sequence = list(_sequence)
        self._sequence = _sequence
        self._names = list(set(self._sequence + kwargs.get('names', [])))
        self._positions = kwargs.get('positions', np.array([]))
        self._edges = kwargs.get('edges', [])
        self._bonds = kwargs.get('bonds', [])

    @property
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
    def names(self) -> typing.List[str]:
        return self._names

    @names.setter
    def names(self, value):
        assert isinstance(value, (list, tuple, set))
        self._names = value

    def add_names(self, value):
        if isinstance(value, (list, tuple, set)):
            self._names += list(value)
        elif isinstance(value, str):
            self._names.append(value)
        else:
            logger.error(
                f'When adding names, ensure that they are strings '
                f'or iters of strings, at the moment they are {type(value)}'
            )

    @property
    def bonds(self):
        return self._bonds

    def add_bond(self, *args, **kwargs):
        """Add TopologyBond or args for it"""

        if len(args) != 0:
            if isinstance(args[0], list):
                bonds = args[0]
                for bond in bonds:
                    self._bonds.append(TopologyBond(**bond))
                return

            elif isinstance(args[0], TopologyBond):
                bond = args[0]
            else:
                bond = TopologyBond(*args, **kwargs)
        else:
            bond = TopologyBond(**kwargs)

        self._bonds.append(bond)

    @property
    def graph(self) -> nx.Graph:
        """Uses NetworkX to get graph of the particles and bonds"""
        g = nx.Graph()
        for edge in self._edges:
            # add edges (nodes are added automatically)
            g.add_edge(edge[0], edge[1])

        # add all the nodes in case any were left out
        # to check that the graph is connected (it must be connected)
        # use self.connected
        for i, _ in enumerate(self.positions):
            g.add_node(i)

        return g

    @property
    def connected(self) -> bool:
        return nx.is_connected(self.graph)

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
            try:
                assert set(diffusion_dictionary.keys()).intersection(set(self.names)) != 0
            except AssertionError:
                logger.error(
                    f'The keys in the diffusion dictionary are: {list(diffusion_dictionary.keys())}'
                    f' but should be {list(set(self.names))}!'
                )
            return diffusion_dictionary

        elif diffusion_constant:
            result = {}
            names = set(self.names)
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
        # use property to make sure that the topology
        # is actually connected before adding it to the simulation
        assert self.connected

        # Add to simulation using its own method
        topology = simulation.add_topology(
            self.top_type,
            self.sequence,
            self.positions
        )

        # add the bonds connecting the network
        for atoms in self.edges:
            topology.get_graph().add_edge(atoms[0] + shift, atoms[1] + shift)
