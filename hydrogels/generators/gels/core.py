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

from typing import List

import readdy

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
        system,
        released: str = 'released',
        reaction_type: str = 'new',
        rate: float = 1e-3
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

        def function_2(topology):
            recipe = readdy.StructuralReactionRecipe(topology)
            graph = topology.get_graph()
            for edge in graph.edges():
                v1, v2 = edge[0], edge[1]
                types = [topology.particles[v1.particle_index].type]
                types.append(topology.particles[v2.particle_index].type)
                if types[0] == self.unbonded or types[1] == self.unbonded:
                    for i, v in enumerate([v1, v2]):
                        index = v.particle_index
                        if types[i] == self.unbonded:
                            n = 0
                            for neighbour in v:
                                n += 1
                            if n == 0:
                                # if no neighbours, release particle from
                                # topology and change to released
                                recipe.change_particle_type(
                                    topology.particles[index],
                                    released
                                )
                                recipe.separate_vertex(index)
                                break
                            else:
                                # if there are neighbours,
                                recipe.change_particle_type(
                                    topology.particles[index],
                                    self.monomer
                                )
                                recipe.remove_edge(edge)
                                break


            return recipe

        reaction_types = {
            'old': function,
            'new': function_2
        }

        system.topologies.add_structural_reaction(
            'decay',
            topology_type=self.top_type,
            reaction_function=reaction_types[reaction_type],
            rate_function=lambda x: rate,
        )

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
