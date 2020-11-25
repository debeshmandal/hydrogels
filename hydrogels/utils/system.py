#!/usr/bin/env python
"""
Objects for handling commonly used high-level readdy systems
"""
import typing
import os

import numpy as np
import pandas as pd
import readdy

from readdy.api.reaction_diffusion_system import ReactionDiffusionSystem

from .topology import Topology

from ..utils.logger import Logger
logger = Logger(__name__)

class Potential:
    def __init__(self, kind, atom_1, atom_2, **kwargs):
        self.kind = kind
        self.atoms = [atom_1, atom_2]
        self.settings = kwargs

    def __repr__(self):
        return f"{self.kind.upper()}({'<>'.join(self.atoms)}; {', '.join([f'{key}:{value}' for key, value in self.settings.items()])})"

    def register(self, system):
        if self.kind == 'lj':
            system.potentials.add_lennard_jones(
                self.atoms[0],
                self.atoms[1],
                m=self.settings.get('m', 12),
                n=self.settings.get('n', 6),
                shift=True,
                epsilon=self.settings['epsilon'],
                sigma=self.settings['sigma'],
                cutoff=self.settings['cutoff'],
            )

class PotentialManager:
    """Class that ensures all of the correct potentials are used"""
    def __init__(self, system: "System"):
        self.system = system
        self._potentials = []

    @property
    def species(self):
        _species = list(self.system._species.keys())
        _deep_names = [i.names for i in self.system.topology_list]
        _names = []
        for name in _deep_names:
            _names.append(name)
        return _species + _names

    @property
    def potentials(self):
        return self._potentials

    def add(self, kind, atom_1, atom_2, **kwargs):
        """Adds a potential to be registered"""

        species = self.species.copy()

        if atom_1 == 'all':
            atom_1 = species

        if atom_2 == 'all':
            atom_2 = species

        if isinstance(atom_1, str):
            assert atom_1 in species
            atom_1 = [atom_1]
        
        if isinstance(atom_2, str):
            assert atom_2 in species
            atom_2 = [atom_2]

        for i in atom_1:
            for j in atom_2:
                self._potentials.append(Potential(kind, i, j, **kwargs))

    def configure(self):
        for potential in self.potentials:
            potential.register(self.system)

class System(ReactionDiffusionSystem):
    """
    Wrapper for a ReaDDy system
    """
    def __init__(self, box):
        super().__init__(box)
        self._topologies = []
        self.manager = PotentialManager(self)
        self._species = {}

    @property
    def potential_list(self):
        return self.manager.potentials
        
    @property
    def topology_list(self):
        return self._topologies

    @property
    def species_list(self):
        return list(self._species)

    def configure_potentials(self):
        """Shortcut to configuring the PotentialManager instance"""
        self.manager.configure()

    def insert_species(self, name: str, D: float, positions: np.ndarray, overwrite: bool = False):
        """Registers the name and positions of a new species
        """
        if name not in self._species:
            self.add_species(name, D)
            self._species[name] = positions
        elif overwrite:
            self._species[name] = positions
        else:
            logger.error(f'Trying to overwrite {name} but positions already exist for it!')
        return

    def insert_topology(self, topology : Topology, **kwargs):
        """
        Takes an instance of hydrogels.Topology and adds the following
        features to the system:
            - topology type e.g. polymer
            - topology species e.g. head, D=5; core, D=5;

        It does not add:
            - potentials
            - reactions

        Either diffusion_constant : float or diffusion_dictionary : dict
        must be provided as keyword arguments
        """

        # check if topology type exists
        # if not then add
        try:
            self.topologies.add_type(topology.top_type)
        except ValueError:
            pass

        # do the same for the topology species
        items = topology.species(**kwargs).items()
        logger.debug(items)
        for name, D in items:
            try:
                self.add_topology_species(name, diffusion_constant=D)
                # if name not in self._species: self._species.append(name)
            except ValueError:
                logger.debug(f'{name} is already registered as a topology species')

        if topology.bonds:
            for bond in topology.bonds:
                bond.register(self)
        else:
            logger.error('Cannot find any registered bonds when adding topology!')
                
        # store in system - be aware that storing this information
        # may cause unnecessary memory usage
        self._topologies.append(topology)

    def initialise_simulation(self, fout='_out.h5', checkpoint: bool = None):
        self.manager.configure()
        simulation = self.simulation()

        if checkpoint:
            # implement loading particles from checkpoint
            raise NotImplementedError

        simulation.output_file = fout
        if os.path.exists(simulation.output_file):
            os.remove(simulation.output_file)


        # add species from dictionary
        for species, positions in self._species.items():
            simulation.add_particles(species, positions)

        # 
        for top in self.topology_list:
            top.add_to_sim(simulation)
        return simulation

    