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

class System(ReactionDiffusionSystem):
    """
    Wrapper for a ReaDDy system
    """
    def __init__(self, box):
        super().__init__(box)
        self._topologies = []
        self._reactions = []
        self._potentials = []
        self._species = []

    @property
    def potential_list(self):
        return self._potentials
        
    @property
    def topology_list(self):
        return self._topologies

    @property
    def reaction_list(self):
        return self._reactions

    @property
    def species_list(self):
        return self._species

    def insert_particles(self):
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
        for name, D in topology.species(**kwargs).items():
            try:
                self.add_topology_species(name, diffusion_constant=D)
                if name not in self._species: self._species.append(name)
            except ValueError:
                pass
                

        # store in system - be aware that storing this information
        # may cause unnecessary memory usage
        self._topologies.append(topology)

    def initialise_simulation(self, fout='_out.h5'):
        simulation = self.simulation()
        simulation.output_file = fout
        if os.path.exists(simulation.output_file):
            os.remove(simulation.output_file)
        for top in self.topology_list:
            top.add_to_sim(simulation)
        return simulation

    