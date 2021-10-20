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

import yaml

from softnanotools.logger import Logger
logger = Logger('POLYMER')

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
    monomer: str = 'A',
    box: float = 25.0
) -> List[Topology]:
    result = []
    for i in range(N):
        x, y, z = np.random.random(3) * box - (box / 2)
        positions = np.array([
            [x, y, z],
            [x+1.0, y, z],
            [x+2.0, y, z],
            [x+3.0, y, z],
            [x+4.0, y, z],
        ])
        molecule = Topology(
            top_type,
            sequence=[monomer] * 5,
            edges=[(0, 1), (1, 2), (2, 3), (3, 4)],
            positions=positions,
        )
        result.append(molecule)
    return result

def create_system(
    box: float = 25.0,
    diffusion_dictionary: dict = DEFAULT_DICTIONARY,
    reaction_radius: float = 1.0,
    reaction_rate: float = 1.0,
    **kwargs,
):
    system = System([box, box, box], units=None)

    # register species
    system.add_species('C', diffusion_dictionary['C'])
    system.add_species('E', diffusion_dictionary['E'])

    # register topology species
    system.add_topology_species('B', diffusion_dictionary['B'])
    system.add_topology_species('A', diffusion_dictionary['A'])

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
            if 'B' in types:
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
                    return recipe

                elif topology.particle_type_of_vertex(edge[1]) == 'B':
                    recipe.remove_edge(edge[0], edge[1])
                    recipe.change_particle_type(edge[1], 'A')
                    logger.debug('Structural 3B')
                    return recipe

        return recipe

    system.topologies.add_structural_reaction(
        name="BondBreaking",
        topology_type="molecule",
        reaction_function=reaction_function,
        rate_function=lambda x: 10000.,

    )

    return system

def run_simulation(
    name: str,
    stride: int = 100,
    timestep: float = 0.01,
    length: int = 10000,
    **kwargs
) -> Path:
    # run equilibration
    logger.info('Running equilibration...')
    # insert code here
    system = create_system(**kwargs)#, reaction=False)
    simulation = system.simulation()

    box = kwargs['box']
    simulation.add_particles(
        'E',
        np.random.rand(kwargs['enzymes'], 3) * box - (box / 2)
    )

    # add topologies
    topologies = create_topologies(kwargs['molecules'], box=box)
    for topology in topologies:
        topology.add_to_sim(simulation)

    #output = Path(f'{name}.h5')
    #if output.exists():
    #    output.unlink()
    #simulation.output_file = str(output.absolute())

    #simulation.make_checkpoints(
    #    stride=stride,
    #    output_directory="checkpoints/",
    #    max_n_saves=1
    #)
    #simulation.evaluate_topology_reactions = False
    #simulation.observe.particles(stride)
    #simulation.observe.topologies(stride)
    #simulation.record_trajectory(stride)
    #simulation.run(5 * stride, timestep)
    #logger.info('Done!')

    # run proper simulaton
    logger.info('Configuring simulation...')
    #system = create_system(**kwargs)
    output = Path(f'{name}.h5')
    if output.exists():
        output.unlink()

    simulation.output_file = str(output.absolute())

    #simulation = system.simulation(output_file=str(output.absolute()))

    # skip adding particles since these will be loaded
    # add_particles(simulation, **kwargs)

    #simulation.load_particles_from_latest_checkpoint(
    #    'checkpoints/'
    #)

    #logger.info('Loaded particles successfully from checkpoint')#

    #output = Path(f'{name}.h5')
    #if output.exists():
    #    output.unlink()
    #simulation = system.simulation(output_file=str(output.absolute()))

    # include observables
    simulation.observe.particles(stride)
    simulation.observe.topologies(stride)
    simulation.record_trajectory(stride)
    simulation.reaction_handler = 'Gillespie'

    logger.info(f'Running simulation {name}...')
    simulation.run(length, timestep)
    logger.info('Done!')
    return output

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

def gather_results(targets: List[Path]) -> pd.DataFrame:
    results = pd.DataFrame()
    dfs = {
        'A': pd.DataFrame(),
        'E': pd.DataFrame(),
        'B': pd.DataFrame(),
        'C': pd.DataFrame()
    }

    for i, target in enumerate(targets):
        data = pd.read_csv(target)
        if i == 0:
            results['t'] = data['t']

        for kind in dfs:
            dfs[kind][i] = data[kind]

    for kind in dfs.keys():
        results[f'{kind}_mean'] = dfs[kind].mean(axis=1)
        results[f'{kind}_std'] = dfs[kind].std(axis=1)

    return results

def plot_final(data: pd.DataFrame, name: str = 'polymer'):
    fig, ax = plt.subplots()
    params = dict(
        markevery=len(data) // 30 if len(data) > 50 else 5,
        errorevery=len(data) // 30 if len(data) > 50 else 5,
        capsize=2
    )
    ax.errorbar(
        data['t'],
        data['A_mean'],
        yerr=data['A_std'],
        fmt='bx-',
        label='A',
        **params
    )
    ax.errorbar(
        data['t'],
        data['B_mean'],
        yerr=data['B_std'],
        fmt='ro-',
        label='B',
        **params
    )

    ax.errorbar(
        data['t'],
        data['C_mean'],
        yerr=data['C_std'],
        fmt='go-',
        label='C',
        **params
    )

    ax.plot(data['t'], data['E_mean'], 'k:', label='E')


    ax.set_xlabel('Timestep', fontsize='xx-large')
    ax.set_ylabel('N', fontsize='xx-large')
    ax.legend(frameon=False, fontsize='x-large')
    fig.tight_layout()
    fig.savefig(f'{name}.png')
    data.to_csv(f'{name}.csv', index=False)
    return

def main(
    settings: str,
    run: bool = False,
    seeds: int = 5,
    name: str = 'monatomic',
    **kwargs
):
    logger.info('Running polymer...')

    with open(settings, 'r') as f:
        parameters = yaml.safe_load(f)
    # insert code here
    for seed in range(1, seeds + 1, 1):
        prefix = f'{name}.{seed}'
        if run:
            traj = run_simulation(prefix, **parameters)
            analyse_trajectory(
                traj,
                output=f'{prefix}.csv',
                timestep=parameters['timestep']
            )
        else:
            logger.info('Skipping simulation because --run was not passed!')
            break

    results = gather_results(Path().glob(f'{name}.*.csv'))
    logger.info(results)
    plot_final(results, name=name)
    logger.info('All Done!')

    logger.info('Done!')
    return

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Enzymatic reaction -A-A-A- + E -> xC + E using ReaDDy'
    )
    parser.add_argument('settings', default='settings.yml')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('-s', '--seeds', default=5, type=int)
    parser.add_argument('-n', '--name', default='polymer')
    main(**vars(parser.parse_args()))