#!/usr/bin/env python
"""diatomic.py - prototype bond breaking reactions:

Uses hydrogels to configure the following system

2 reactions:
    A-A + E -> A-B + E (spatial) r=2.0, k=1.0
    A-B -> C + C (structural) k=1.0

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
            [x+1.0, y, z]
        ])
        molecule = Topology(
            top_type,
            sequence=[monomer] * 2,
            edges=[(0, 1)],
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

    # register A-B -> C + C reaction
    def reaction_function(topology):
        recipe = readdy.StructuralReactionRecipe(topology)
        vertices = topology.get_graph().get_vertices()
        types = sorted([topology.particle_type_of_vertex(v) for v in vertices])
        if types[0] == 'A' and types[1] == 'B':
            recipe.separate_vertex(0)
            recipe.change_particle_type(vertices[0], 'C')
            recipe.change_particle_type(vertices[1], 'C')

        return recipe

    system.topologies.add_structural_reaction(
        name="BondBreaking",
        topology_type="molecule",
        reaction_function=reaction_function,
        rate_function=lambda x: 10.0,

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
    simulation.add_particles('E', np.random.rand(50, 3) * 12.5)

    # add topologies
    topologies = create_topologies(100)
    for topology in topologies:
        topology.add_to_sim(simulation)

    output = Path('_out.h5')
    if output.exists():
        output.unlink()
    simulation.output_file = str(output.absolute())
    simulation.observe.particles(1000)
    simulation.run(100000, 0.0001)

    results = analyse_trajectory(output, output='test.csv', timestep =0.0001)
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
        description='diatomic.py - auto-generated by softnanotools'
    )
    main(**vars(parser.parse_args()))
