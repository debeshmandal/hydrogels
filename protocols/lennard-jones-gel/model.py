#!/usr/bin/env python
"""
Reads a trajectory to determine the degradation rate
of a hydrogel and applies an analytical model to which a 
comparison can be made.
"""
import hydrogels
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import hydrogels.theory.models.simulations.lennard_jones

LennardJonesSimulation = hydrogels.theory.models.simulations.lennard_jones.LennardJones

from hydrogels.utils.logger import Logger
logger = Logger('model.py')

def _extract_data(fname : str) -> dict:
    df = pd.read_csv('fname')
    data = {
        'particles' : df,
        'N' : max(df.iloc[:, 0])
    }
    return data

def _plot_trajectory(
    ax: plt.Axes, 
    data: pd.DataFrame
) -> plt.Line2D:
    line = ax.plot(data.iloc[:, 0], 'k+:')
    return line

def _model(
    N, 
    conc, 
    density, 
    **kwargs
) -> LennardJonesSimulation:
    return LennardJonesSimulation(
        kwargs['timestep'],
        N,
        sig=kwargs['sig'],
        eps=kwargs['eps'],
        rc=kwargs['rc'],
        beta=kwargs['beta'],
        c0=conc,
        KV=kwargs['KV'],
        nV=density,
    )

def _plot_model(
    ax: plt.Axes, 
    model: LennardJonesSimulation
) -> plt.Line2D:
    return

def main(**kwargs):

    logger.debug(f'Creating Axes...')
    fig, ax = plt.subplots()

    logger.debug(f'Plotting Trajectory...')
    fname = kwargs['particles_file']
    
    logger.info(f'Using file: {fname}')   
    data = _extract_data(fname) 
    _plot_trajectory(ax, data['gel'])

    logger.debug(f'Running _model...')
    N = data['N']
    conc = data['N'] / kwargs['box'] ** 3
    density = data['density']
    model = _model(N, conc, density, **kwargs)
    logger.debug(f'Created Model: {model.string}')

    n_timesteps = kwargs['timestep'] * data['steps']
    logger.debug(
        f'Using {n_timesteps} timesteps'
        f' with dt={kwargs["timestep"]}')
    model.run(n_timesteps)
    logger.debug(f'Plotting Model...')
    _plot_model(ax)

    fout = kwargs.get('plot_file', False)
    if fout:
        logger.info(f'Saving plot to {fout}...')
        fig.savefig()
        logger.info(f'Save successful!')

    if kwargs.get('show', False):
        logger.info('Showing plot...')
        plt.show()

    return

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()

    # files and plotting options
    parser.add_argument('--json', required=True)
    parser.add_argument('--plot-file', required=False, default=None)
    parser.add_argument('--show', action='store_true')
    parser.add_argument('--enforce', action='store_true')

    args = vars(parser.parse_args())
    main(**args)