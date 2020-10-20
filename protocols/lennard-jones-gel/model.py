#!/usr/bin/env python
"""
Reads a trajectory to determine the degradation rate
of a hydrogel and applies an analytical model to which a 
comparison can be made.
"""
import json 
import hydrogels
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import hydrogels.theory.models.simulations.lennard_jones

LennardJonesSimulation = hydrogels.theory.models.simulations.lennard_jones.LennardJones

from hydrogels.utils.logger import Logger
logger = Logger('model.py')

def _extract_data(fname : str) -> dict:
    df = pd.read_csv(fname)
    logger.debug(f'Particles:\n{df.head()}')
    data = {
        'particles' : df,
        'N' : max(df.iloc[:, 0])
    }
    return data

def _plot_trajectory(
    ax: plt.Axes, 
    data: pd.DataFrame,
    timestep: float,
    stride: float,
) -> plt.Line2D:
    time = np.arange(0, len(data)) * timestep * stride
    line = ax.plot(time, data.iloc[:, 0], 'k+:', label='Simulation Trajectory')
    return line

def _model(
    N, 
    conc, 
    density,
    simulation,
    **kwargs
) -> LennardJonesSimulation:
    return LennardJonesSimulation(
        simulation['timestep'],
        N,
        sig=simulation['lj_sig'],
        eps=simulation['lj_eps'],
        rc=simulation['lj_cutoff'],
        beta=0.4,
        c0=conc,
        nV=density,
        thickness=simulation['reaction_radius'],
        rate=simulation['enzyme_number']/simulation['reaction_rate'],
    )

def _plot_model(
    ax: plt.Axes, 
    model: LennardJonesSimulation
) -> plt.Line2D:
    temp = model.history.dataframe
    skip = len(temp) // 100
    temp = temp.iloc[::skip]
    logger.debug(f'Using temp with {len(temp)} rows')
    ax.plot(temp['t'], temp['N'], 'k-', label='Analytical Model')
    return

def main(**kwargs):

    logger.debug(f'Creating Axes...')
    fig, ax = plt.subplots()
    ax.set_xlabel(r"Time [$\tau$]", fontsize='x-large')
    ax.set_ylabel(r"Number of Particles in Gel", fontsize='x-large')

    f_json = kwargs['json']
    logger.info(f'Using JSON file {f_json}')
    with open(f_json, 'r') as f:
        settings = json.load(f)

    logger.debug(f'JSON Data: {json.dumps(settings, indent=2)}')
    
    logger.debug(f'Plotting Trajectory...')
    f_particles = settings['trajectory']['f_particles']
    logger.info(f'Using particles file: {f_particles}')   
    data = _extract_data(f_particles)
    dt = settings['simulation']['timestep']
    stride = settings['simulation']['stride']
    _plot_trajectory(ax, data['particles'], dt, stride)

    logger.debug(f'Running _model...')
    N = data['N']
    conc = data['N'] / settings['simulation']['box'] ** 3
    density = settings['trajectory']['gel_density']

    n_timesteps =  stride * settings['simulation']['length']
    logger.debug(
        f'Using {n_timesteps} timesteps'
        f' with dt={dt}')

    model = _model(N, conc, density, settings['simulation'])
    #logger.debug(f'Created Model: {model.string}')
    model.run(n_timesteps)
    logger.info(f'Ran model and returned history:\n{model.history.dataframe}')
    logger.debug(f'Plotting Model...')
    _plot_model(ax, model)
    ax.legend(frameon=False, fontsize='x-large')

    fout = kwargs.get('plot_file', False)
    if fout:
        logger.info(f'Saving plot to {fout}...')
        fig.savefig(fout)
        logger.info(f'Save successful!')

    if kwargs.get('show', False):
        logger.info('Showing plot...')
        plt.show()

    f_model = kwargs.get('model_file', False)
    if f_model:
        logger.info(f'Writing model history to {f_model}')
        model.history.dataframe.to_csv(f_model, index=False)

    return

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()

    # files and plotting options
    parser.add_argument('--json', required=True)
    parser.add_argument('--plot-file', required=False, default=None)
    parser.add_argument('--model-file', required=False, default=None)
    parser.add_argument('--show', action='store_true')
    parser.add_argument('--enforce', action='store_true')

    args = vars(parser.parse_args())
    main(**args)