#!/usr/bin/env python
"""Contains structural reaction classes for use in ReaDDy to declare
structural topology reactions

Classes:
    BondBreaking: container for bond breaking schemes
"""

from typing import Callable
import readdy

from softnanotools.logger import Logger
logger = Logger(__name__)

class StructuralReaction:
    def __init__(
        self,
        reaction_function,
        name: str = 'reaction',
        topology_type: str = 'molecule',
        rate_function: Callable = lambda x: 10000.0,
    ):
        self.name = name
        self.topology_type = topology_type
        self.reaction_function = reaction_function
        self.rate_function = rate_function

    def __call__(self, topology):
        return self.reaction_function(topology)

    def register(self, system: readdy.ReactionDiffusionSystem):
        """Registers the structural reaction to a given system"""
        system.topologies.add_structural_reaction(
            self.name,
            topology_type=self.topology_type,
            reaction_function=self,
            rate_function=self.rate_function,
        )
        return

class BondBreaking:
    """Class to store different Bond Breaking structural reactions
    for use in ReaDDy.

    Converts bonded [reactant] topology particles to [product] particles
    via [intermediate] topology particles

    [intermediate] topology particles are typically created in spatial
    reactions, and BondBreaking provides a mechanism and functionality
    to convert these to [product] particles.

    There are currently two reaction schemes:
        - polymer
            Generic Bond breaking with an arbitrary number of particles
            in a topology
        - diatomic:
            Bond breaking when a topology has only two particles

    Example:

    ```python
    reaction = BondBreaking('R', 'I', 'P').polymer
    ...
    system.topologies.add_structural_reaction(
        name=reaction.name
        topology_type=reaction.topology_type
        reaction_function=reaction
        rate_function=reaction.rate_function
    )
    ```
    It is quite easy to overwrite the `name`, `topology_type`, and
    `rate_function` parameters manually, however we believe that users
    may prefer storing their reaction metadata within the same class
    as their reaction.

    Parameters:
        reactant: name of reactant topology species
        intermediate: name of reactant topology species
        product: name of reactant topology species
        name (optional): name of reaction type
        rate_function (optional): rate function for use in ReaDDy
        topology_type (optional): topology to execute reaction on

    Attributes:
        reactant: name of reactant topology species
        intermediate: name of reactant topology species
        product: name of reactant topology species
        name: name of reaction type
        rate_function: rate function for use in ReaDDy
        topology_type: topology to execute reaction on

        diatomic: Bond breaking when a topology has only two particles
        polymer: Bond breaking with an arbitrary number of particles

    """
    def __init__(
        self,
        reactant,
        intermediate,
        product,
        name: str = 'bond_breaking',
        rate_function: Callable = lambda x: 10000,
        topology_type: str = 'molecule',
    ):
        # important variables
        self.reactant = reactant
        self.intermediate = intermediate
        self.product = product

        # optional variables that are useful for storage
        # but not essential, and easy to override
        self.name = name
        self.rate_function = rate_function
        self.topology_type = topology_type

    @property
    def diatomic(self) -> Callable:
        """Returns a bond breaking function that converts a single
        diatomic molecule to two product particles. The diatomic
        molecule should contain a topology particle that corresponds
        to BondBreaking.intermediate"""
        def fn(topology) -> readdy.StructuralReactionRecipe:
            # get reaction recipe
            recipe = readdy.StructuralReactionRecipe(topology)

            # get the vertices of the topology
            vertices = topology.get_graph().get_vertices()

            # sort types (either A or B) for easier analysis
            types = [topology.particle_type_of_vertex(v) for v in vertices]

            # if B is present then change both particles to C
            # and delete bond by using recipe.separate_vertex
            if self.intermediate in types:
                recipe.separate_vertex(0)
                recipe.change_particle_type(vertices[0], self.product)
                recipe.change_particle_type(vertices[1], self.product)

            # return the configured recipe
            return recipe
        return StructuralReaction(
            fn,
            name=self.name,
            topology_type=self.topology_type,
            rate_function=self.rate_function
        )

    @property
    def polymer(self) -> Callable:
        def fn(topology) -> readdy.StructuralReactionRecipe:
            recipe = readdy.StructuralReactionRecipe(topology)
            # it is possible for there to be a lone particle in a topology
            # when reactions happen very quickly, this step ensures that
            # these are converted to [product] particles which are not
            # topology-bound
            vertices = topology.get_graph().get_vertices()
            if len(vertices) == 1:
                recipe.separate_vertex(0)
                recipe.change_particle_type(vertices[0], self.product)

            # register R-I -> P + P reaction
            elif len(vertices) == 2:
                types = [topology.particle_type_of_vertex(v) for v in vertices]
                if self.intermediate in types:
                    recipe.separate_vertex(0)
                    recipe.change_particle_type(vertices[0], self.product)
                    recipe.change_particle_type(vertices[1], self.product)

            # register -R-I-R- -> -R + R-R-
            else:
                # insert reaction
                edges = topology.get_graph().get_edges()
                for edge in edges:
                    if topology.particle_type_of_vertex(edge[0]) \
                        == self.intermediate:

                        # remove the bond and convert back to reactant
                        recipe.remove_edge(edge[0], edge[1])
                        recipe.change_particle_type(edge[0], self.reactant)

                    elif topology.particle_type_of_vertex(edge[1]) \
                        == self.intermediate:

                        # do the same but with the other particle
                        # since that is the one that is an intermediate
                        recipe.remove_edge(edge[0], edge[1])
                        recipe.change_particle_type(edge[1], self.reactant)
            return recipe
        return StructuralReaction(
            fn,
            name=self.name,
            topology_type=self.topology_type,
            rate_function=self.rate_function
        )

if __name__ == '__main__':
    import doctest
    doctest.testmod()
