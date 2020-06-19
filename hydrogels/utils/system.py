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

import hydrogels

class System(ReactionDiffusionSystem):
    """
    Wrapper for a ReaDDy system
    """
    def __init__(self, box):
        super(box)
        self._topologies = []
        self._reactions = []
        self._potentials = []

    @property
    def potentials(self):
        return self._potentials
        
    @property
    def topologies(self):
        return self._topologies

    @property
    def reactions(self):
        return self._reactions

    def add_atoms(self):
        return

    def add_topology(self, topology : hydrogels.Topology):
        if True:
            raise NotImplementedError

        # check if topology type exists
        # if not then add
        self.topologies.add_type(topology.top_type)

        # do the same for the topology species
        self.add_topology_species('core', diffusion_constant=1.0)
        self.add_topology_species('head', diffusion_constant=1.0)

        # add to simulation
        topology.add_to_sim(self.simulation)
        return

    def initialise_simulation(self, fout='_out.h5'):
        simulation = self.simulation
        simulation.output_file = fout
        if os.path.exists(simulation.output_file):
            os.remove(simulation.output_file)
        return simulation

    