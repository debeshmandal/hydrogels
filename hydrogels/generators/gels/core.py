#!/usr/bin/env python
"""
Gels systems containing of polymers. This package lives above polymers.py in the
molecule hierarchy.
"""
import random
from itertools import product

import pandas as pd
import numpy as np
from scipy.spatial.distance import pdist, squareform

from ...utils.topology import Topology
from ..polymers import LinearPolymer, CrosslinkingPolymer

class Gel(Topology):
    """
    A Gel is a ReaDDy Topology that can be used
    to generate systems to model hydrogels.
    """
    def __init__(
        self,
        top_type,
        positions: np.ndarray = None,
        monomer: str = 'monomer',
        unbonded: str = 'unbonded',
    ):

        self.monomer = monomer
        self.unbonded = unbonded

        if isinstance(positions, (np.ndarray, list, tuple)):
            super().__init__(
                top_type,
                positions=positions,
                sequence=len(positions) * [monomer],
                names=[self.monomer, self.unbonded]
            )

        else:
            super().__init__(top_type)

    def configure_bonds(self, kind, **kwargs):

        # configure normal bond like normal
        self.add_bond(kind, self.monomer, self.monomer, **kwargs)

        # set force constant to zero for unbonded topology particles
        ghost_bond = {
            'force_constant': 0.0,
            'length': 1.0
        }
        self.add_bond('harmonic', self.monomer, self.unbonded, **ghost_bond)
        self.add_bond('harmonic', self.unbonded, self.unbonded, **ghost_bond)
        return

    def register_decay(
        self, 
        system, 
        released: str = 'released', 
        rate = 1e-3
    ):
        """Registers the decay of unbonded topology particles 
        to released particles"""

        def function(topology):
            recipe = readdy.StructuralReactionRecipe(topology)
            index = np.random.randint(0, len(topology.particles))
            if topology.particles[index].type == self.unbonded:
                recipe.separate_vertex(index)
                recipe.change_particle_type(index, released)
            return recipe

        system.topologies.add_structural_reaction(
            'decay',
            topology_type=self.top_type,
            reaction_function=function,
            rate_function=lambda x: 1e-3,
        )

        return

    def register_degradation(
        system, 
        enzyme: str = 'enzyme',
        rate: float = 1e-3,
        radius: float = 2.0
    ):

        reaction = (
            f'reaction: {self.top_type}({self.monomer})'
            f'+({enzyme}) -> {self.top_type}({self.unbonded})+({enzyme})'
        )

        system.reactions.add(
            reaction, 
            rate=rate, 
            radius=radius
        )

        return

