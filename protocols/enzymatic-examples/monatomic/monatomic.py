#!/usr/bin/env python
"""Enzymatic reaction A + E -> B + E using ReaDDy"""
from pathlib import Path
from typing import List, Union
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yaml

from softnanotools.logger import Logger
logger = Logger('MONATOMIC')

import readdy

def create_system(
    box: float = 25.0,
    diffusion_dictionary: dict = {
        'A': 1.0,
        'B': 1.0,
        'E': 1.0,
    },
    reaction_radius: float = 2.0,
    reaction_rate: float = 1.0,
    spring_constant: float = 5.0,
    spring_length: float = 1.0,
    reaction: bool = True,
    **kwargs,
) -> readdy.ReactionDiffusionSystem:
    system = readdy.ReactionDiffusionSystem(
        [box, box, box],
        unit_system=None,
    )
    # add species:

    ## reactant
    for name, diffusion_constant in diffusion_dictionary.items():
        system.add_species(name, diffusion_constant)

    ## add reaction:
    if reaction:
        system.reactions.add(
            f'reaction: A + ({reaction_radius:.2f})E -> B + E',
            rate=reaction_rate
        )

    ## add potentials:
    for pair in [
        ['A', 'A'],
        ['A', 'B'],
        ['A', 'E'],
        ['B', 'B'],
        ['B', 'E'],
        ['E', 'E'],
    ]:
        system.potentials.add_harmonic_repulsion(
            *pair,
            force_constant=spring_constant,
            interaction_distance=spring_length
        )

    return system

def add_particles(
    simulation: readdy.Simulation,
    box: float = 25.0,
    particles: int = 500,
    enzymes: int = 50,
    **kwargs
):
    """Add 100 A particles and 20 E particles"""
    for name, N in [('A', particles), ('E', enzymes)]:
        positions = np.random.rand(N, 3) * (box / 2)
        simulation.add_particles(name, positions)
    return

def run_simulation(
    name: str,
    stride: int = 100,
    timestep: float = 0.01,
    length: int = 10000,
    **kwargs
) -> Path:
    # run equilibration
    logger.info('Running equilibration...')
    system = create_system(**kwargs, reaction=False)
    output = Path(f'{name}.h5')
    if output.exists():
        output.unlink()
    simulation = system.simulation(output_file=str(output.absolute()))
    add_particles(simulation, **kwargs)
    simulation.make_checkpoints(
        stride=stride,
        output_directory="checkpoints/",
        max_n_saves=1
    )
    simulation.evaluate_topology_reactions = False
    simulation.run(100, timestep)
    logger.info('Done!')

    # run proper simulaton
    logger.info('Configuring simulation...')
    system = create_system(**kwargs, reactions=False)
    output = Path(f'{name}.h5')
    if output.exists():
        output.unlink()
    simulation = system.simulation(output_file=str(output.absolute()))

    # skip adding particles since these will be loaded
    # add_particles(simulation, **kwargs)

    simulation.load_particles_from_latest_checkpoint(
        'checkpoints/'
    )

    logger.info('Loaded particles successfully from checkpoint')
    # include observables
    simulation.observe.particles(stride)
    logger.info(f'Running simulation {name}...')
    simulation.record_trajectory(stride)
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
        'E': []
    }
    for row in particles[1]:
        numbers['A'].append(len(row[row == particle_types['A']]))
        numbers['E'].append(len(row[row == particle_types['E']]))
        numbers['B'].append(len(row[row == particle_types['B']]))

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
    }

    for i, target in enumerate(targets):
        data = pd.read_csv(target)
        if i == 0:
            results['t'] = data['t']

        for kind in dfs:
            dfs[kind][i] = data[kind]

    for kind in ['A', 'B', 'E']:
        results[f'{kind}_mean'] = dfs[kind].mean(axis=1)
        results[f'{kind}_std'] = dfs[kind].std(axis=1)

    return results

def plot_final(data: pd.DataFrame, name: str = 'monatomic'):
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
    ax.plot(data['t'], data['E_mean'], 'k:', label='E')


    ax.set_xlabel('Timestep', fontsize='xx-large')
    ax.set_ylabel('N', fontsize='xx-large')
    ax.legend(frameon=False, fontsize='x-large')
    fig.tight_layout()
    fig.savefig(f'{name}.png')
    data.to_csv(f'{name}.csv', index=False)
    return

def main(settings: str, run: bool = False, seeds: int = 5, name: str = 'monatomic', **kwargs):
    logger.info('Running monatomic...')
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
    return

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Enzymatic reaction A + E -> B + E using ReaDDy'
    )
    parser.add_argument('settings', default='settings.yml')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('-s', '--seeds', default=5, type=int)
    parser.add_argument('-n', '--name', default='monatomic')
    main(**vars(parser.parse_args()))
