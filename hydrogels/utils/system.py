#!/usr/bin/env python
"""
Objects for handling commonly used high-level readdy systems
"""
import typing
import os
import json

import numpy as np
import pandas as pd
import readdy

from readdy.api.reaction_diffusion_system import ReactionDiffusionSystem

from .topology import Topology

from softnanotools.logger import Logger
logger = Logger(__name__)

class Potential:
    def __init__(self, kind, atom_1, atom_2, **kwargs):
        self.kind = kind
        self.atoms = [atom_1, atom_2]
        self.settings = kwargs

    def __repr__(self):
        return (f"{self.kind.upper()}({'<->'.join(self.atoms)};"
        f" {', '.join([f'{key}:{value}' for key, value in self.settings.items()])})")

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
        for item in _deep_names:
            for name in item:
                _names.append(name)
        return _species + _names

    @property
    def potentials(self):
        return self._potentials

    def add(self, kind, atom_1, atom_2, **kwargs):
        """Adds a potential to be registered"""

        species = self.species.copy()
        logger.debug(species)

        if isinstance(atom_1, str):
            if atom_1 == 'all':
                atom_1 = species
            else:
                # this is commented out because sometimes potentials
                # are registered before species - same as below
                #assert atom_1 in species
                atom_1 = [atom_1]

        for i, a in enumerate(atom_1):
            assert isinstance(a, str), f'{a} should be a string but is not!'
            if isinstance(atom_2, str):
                if atom_2 == 'all':
                    atom_2 = species
                else:
                    #assert atom_2 in species
                    atom_2 = [atom_2]

            for j, b in enumerate(atom_2):
                if j > i: continue
                assert isinstance(b, str), f'{b} should be a string but is not!'
                logger.debug(f'Adding potential with\n\tkind: {kind}\n\ta<->b: {a}<->{b}\n\tkwargs: {json.dumps(kwargs, indent=2)}')
                potential = Potential(kind, a, b, **kwargs.copy())
                logger.debug(f'Potential added: {potential}')
                self._potentials.append(potential)

    def configure(self):
        logger.debug('Configuring potentials...')
        for potential in self._potentials:
            logger.debug(f'Configuring:\n\t{potential}')
            potential.register(self.system)

class System(ReactionDiffusionSystem):
    """
    Wrapper for a ReaDDy system
    """
    def __init__(self, box, unit_system=None, **kwargs):
        super().__init__(box, unit_system=unit_system, **kwargs)
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

    @property
    def topology_species_list(self):
        return [i.names for i in self.topology_list]

    def add_potential(self, *args, **kwargs):
        logger.debug(
            f'Adding potential to system with:\n\targs: {args}\n\tkwargs:{json.dumps(kwargs, indent=2)}'
        )
        self.manager.add(*args, **kwargs)

    def configure_potentials(self):
        """Shortcut to configuring the PotentialManager instance"""
        self.manager.configure()

    def insert_species(self, name: str, D: float, positions: np.ndarray, overwrite: bool = False):
        """Registers the name and positions of a new species
        """
        if name not in self._species:
            try:
                self.add_species(name, D)
            except ValueError:
                logger.debug(f'{name}[{D}] has already been registered')
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

            logger.debug('Cannot find any registered bonds when adding topology!')

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
            if len(positions) != 0:
                simulation.add_particles(species, positions)

        #
        for top in self.topology_list:
            top.add_to_sim(simulation)
        return simulation
