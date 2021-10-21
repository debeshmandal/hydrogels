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

from typing import Callable, List, Union

import readdy

from ...utils.topology import Topology
from ...reactions import BondBreaking, StructuralReaction

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
        sequence: List[str] = None,
        edges: List[tuple] = None,
    ):

        self.monomer = monomer
        self.unbonded = unbonded

        if isinstance(sequence, type(None)):
            sequence = sequence=len(positions) * [monomer]

        if isinstance(positions, (np.ndarray, list, tuple)):
            super().__init__(
                top_type,
                positions=positions,
                sequence=len(positions) * [monomer],
                names=[self.monomer, self.unbonded],
                edges=edges
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
        system: readdy.ReactionDiffusionSystem,
        released: str = None,
        reaction_type: Union[str, StructuralReaction] = 'polymer',
        rate: Union[float, Callable] = None,
    ):
        """Registers the decay of unbonded topology particles
        to released particles to a system

        Parameters:
            system: A ReaDDy system instance
            released: name of the released particle aka the product
            reaction_type: the name or a custom scheme of a reaction type
            rate: constant rate or pre-defined rate function

        """

        if isinstance(reaction_type, StructuralReaction):
            reaction_type.register(system)

        if not released:
            released = 'released'

        name = 'decay'

        def function(topology):
            recipe = readdy.StructuralReactionRecipe(topology)
            index = np.random.randint(0, len(topology.particles))
            if topology.particles[index].type == self.unbonded:
                recipe.separate_vertex(index)
                recipe.change_particle_type(index, released)
            return recipe

        # parse rate options
        if isinstance(rate, Callable):
            rate_function = rate

        if isinstance(rate, (float, int)):
            rate_function = lambda x: rate

        if not rate:
            rate_function = lambda x: 10000.0

        default = StructuralReaction(
            function,
            name=name,
            topology_type=self.top_type,
            rate_function=rate_function
        )

        bond_breaking_instance = BondBreaking(
            self.monomer,
            self.unbonded,
            released,
            name=name,
            topology_type=self.top_type,
            rate_function=rate_function
        )

        reaction_types = {
            'legacy': default,
            'polymer': bond_breaking_instance.polymer,
            'diatomic': bond_breaking_instance.diatomic
        }

        reaction_types[reaction_type].register(system)

        return

    def register_degradation(
        self,
        system,
        enzyme: str = 'enzyme',
        rate: float = 1e-3,
        radius: float = 2.0
    ):

        system.reactions.add_enzymatic(
            name="degradation",
            type_catalyst=enzyme,
            type_from=self.monomer,
            type_to=self.unbonded,
            rate=rate,
            educt_distance=radius
        )

        return
