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

class System(ReactionDiffusionSystem):
    """
    Wrapper for a ReaDDy system
    """
    def __init__(self, box):
        super(box)
        self._atoms = pd.DataFrame()
        self._topologies = pd.DataFrame()

    def add_atoms(self):
        return

    def add_topology(self):
        return

    def initialise_simulation(self, fout='_out.h5'):
        simulation = self.simulation
        simulation.output_file = fout
        if os.path.exists(simulation.output_file):
            os.remove(simulation.output_file)
        return simulation

    