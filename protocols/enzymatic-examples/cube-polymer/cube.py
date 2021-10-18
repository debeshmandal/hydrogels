#!/usr/bin/env python
"""polymer.py - prototype bond breaking reactions:

Uses hydrogels to configure the following system

2 reactions:
    -A-A-A- + E -> -A-B-A- + E (spatial) r=2.0, k=1.0
    { (structural) k=10000...
        -A-B-A- -> -A + A-A-
          A-B   ->  C + C
    }

2 particle_types:
    E (enzyme)
    C (released)

2 topology_particle_types:
    A (monomer)
    B (unbonded)

1 topology_type
    molecule

2 potential_types
    harmonic repulsion (pair; all) r0=1.0, k=2.0
    harmonic bonding (bond; A-A A-B) r0=1.0, k=5.0
"""
from pathlib import Path
from typing import List, Union
import numpy as np
import readdy
import pandas as pd
import matplotlib.pyplot as plt

from softnanotools.logger import Logger
logger = Logger('DIATOMIC')

from hydrogels.utils.system import System
from hydrogels.utils.topology import Topology, TopologyBond

DEFAULT_DICTIONARY = {
    'A': 1.0,
    'B': 1.0,
    'C': 1.0,
    'E': 1.0,
}

def register_bonding(
    system: System,
    monomer: str = 'A',
    unbonded: str = 'B',
    length: float = 1.0,
    force_constant: float = 2.5,
):
    bond = TopologyBond(
        'harmonic',
        monomer,
        monomer,
        length=length,
        force_constant=force_constant
    )
    bond.register(system)

    bond = TopologyBond(
        'harmonic',
        monomer,
        unbonded,
        length=length,
        force_constant=0.0
    )
    bond.register(system)

    bond = TopologyBond(
        'harmonic',
        unbonded,
        unbonded,
        length=length,
        force_constant=0.0
    )
    bond.register(system)
    return

def register_potentials(system: System, spring_constant=2.5, spring_length=1.0):
    for pair in [
        ['A', 'A'],
        ['A', 'B'],
        ['A', 'E'],
        ['A', 'C'],
        ['B', 'B'],
        ['B', 'E'],
        ['B', 'C'],
        ['E', 'E'],
        ['E', 'C'],
        ['C', 'C'],
    ]:
        system.potentials.add_harmonic_repulsion(
            *pair,
            force_constant=spring_constant,
            interaction_distance=spring_length
        )
    return

def create_topologies(
    N: int,
    top_type: str = 'molecule',
    monomer: str = 'A'
) -> List[Topology]:
    result = []
    for i in range(N):
        x, y, z = np.random.random(3) * 12.5
        positions = np.array([
            [x, y, z],
            [x+1.0, y, z],
            [x+1.0, y+1.0, z],
            [x, y+1.0, z],
            [x, y, z+1.0],
            [x+1.0, y, z+1.0],
            [x+1.0, y+1.0, z+1.0],
            [x, y+1.0, z+1.0],
        ])
        molecule = Topology(
            top_type,
            sequence=[monomer] * 8,
            edges=[
                (0, 1),
                (1, 2),
                (2, 3),
                (3, 0),
                (4, 5),
                (5, 6),
                (6, 7),
                (7, 4),
                (0, 4),
                (1, 5),
                (2, 6),
                (3, 7),
            ],
            positions=positions,
        )
        result.append(molecule)
    return result

def create_system(
    box: float = 25.0,
    diffusion_dictionary: dict = DEFAULT_DICTIONARY,
    reaction_radius: float = 2.0,
    reaction_rate: float = 1.0
):
    system = System([box, box, box], units=None)

    # register species
    system.add_species('C', DEFAULT_DICTIONARY['C'])
    system.add_species('E', DEFAULT_DICTIONARY['E'])

    # register topology species
    system.add_topology_species('B', DEFAULT_DICTIONARY['B'])
    system.add_topology_species('A', DEFAULT_DICTIONARY['A'])

    system.topologies.add_type('molecule')

    # register bonding
    register_bonding(system)

    # add potentials
    register_potentials(system)

    # register enzymatic reaction
    system.topologies.add_spatial_reaction(
        f'reaction: molecule(A) + (E) -> molecule(B) + (E)',
        rate=reaction_rate,
        radius=reaction_radius,
    )


    def reaction_function(topology):
        recipe = readdy.StructuralReactionRecipe(topology)

        # it is possible for there to be a lone particle in a topology
        # when reactions happen very quickly, this step ensures that
        # these are converted to C particles which are not topology-bound
        vertices = topology.get_graph().get_vertices()
        if len(vertices) == 1:
            recipe.separate_vertex(0)
            recipe.change_particle_type(vertices[0], 'C')
            logger.debug('Structural 1')

        # register A-B -> C + C reaction
        elif len(vertices) == 2:
            types = [topology.particle_type_of_vertex(v) for v in vertices]
            types = sorted(types)
            if types[0] == 'A' and types[1] == 'B':
                recipe.separate_vertex(0)
                recipe.change_particle_type(vertices[0], 'C')
                recipe.change_particle_type(vertices[1], 'C')
                logger.debug('Structural 2')

        # register -A-B-A- -> -A + A-A-
        else:
            # insert reaction
            edges = topology.get_graph().get_edges()
            for edge in edges:
                if topology.particle_type_of_vertex(edge[0]) == 'B':
                    recipe.remove_edge(edge[0], edge[1])
                    recipe.change_particle_type(edge[0], 'A')
                    logger.debug('Structural 3A')
                elif topology.particle_type_of_vertex(edge[1]) == 'B':
                    recipe.remove_edge(edge[0], edge[1])
                    recipe.change_particle_type(edge[1], 'A')
                    logger.debug('Structural 3B')

        return recipe

    system.topologies.add_structural_reaction(
        name="BondBreaking",
        topology_type="molecule",
        reaction_function=reaction_function,
        rate_function=lambda x: 1000000.,

    )

    return system

def analyse_trajectory(
    fname: Union[str, Path],
    output: Union[str, Path, None] = None,
    timestep: float = 0.01,
) -> pd.DataFrame:
    logger.info('Analysing trajectory...')
    fname = Path(fname).absolute()
    trajectory = readdy.Trajectory(str(fname))
    trajectory.convert_to_xyz(particle_radii={
        'A': 0.25,
        'B': 0.25,
        'C': 0.25,
        'E': 0.25,
    })
    particle_types = trajectory.particle_types
    particles = trajectory.read_observable_particles()

    numbers = {
        't': particles[0] * timestep,
        'A': [],
        'B': [],
        'E': [],
        'C': [],
    }
    for row in particles[1]:
        numbers['A'].append(len(row[row == particle_types['A']]))
        numbers['E'].append(len(row[row == particle_types['E']]))
        numbers['B'].append(len(row[row == particle_types['B']]))
        numbers['C'].append(len(row[row == particle_types['C']]))

    results = pd.DataFrame(numbers)
    if output:
        results.to_csv(output, index=False)
    return results

def main(**kwargs):
    logger.info('Running diatomic...')
    # insert code here
    system = create_system()
    simulation = system.simulation()
    simulation.add_particles('E', np.random.rand(200, 3) * 12.5)

    # add topologies
    topologies = create_topologies(44)
    for topology in topologies:
        topology.add_to_sim(simulation)

    output = Path('_out.h5')
    if output.exists():
        output.unlink()
    simulation.output_file = str(output.absolute())
    simulation.observe.particles(1000)
    simulation.observe.reaction_counts(1000)
    simulation.observe.topologies(1000)
    simulation.record_trajectory(stride=1000)
    simulation.progress_output_stride = 1000
    simulation.run(100000, 0.001)

    results = analyse_trajectory(output, output='test.csv', timestep = 0.001)
    fig, ax = plt.subplots()
    ax.plot(results['t'], results['A'], 'bx-', label='A')
    ax.plot(results['t'], results['B'], 'rs-', label='B')
    ax.plot(results['t'], results['C'], 'go-', label='C')
    ax.plot(results['t'], results['E'], 'k:')
    fig.savefig('test.png')

    logger.info('Done!')
    return

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='polymer.py - auto-generated by softnanotools'
    )
    main(**vars(parser.parse_args()))
