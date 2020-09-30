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

def _model(**kwargs):
    return

def _plot_trajectory(ax):
    return

def _plot_model(ax):
    return

def main(**kwargs):
    folder = kwargs.get('traj_folder')
    prefix = kwargs.get('prefix')

    model = _model(**kwargs)

    fig, ax = plt.subplots()
    _plot_model(ax)
    _plot_trajectory(ax)

    fout = kwargs.get('plot_file', False)
    if fout:
        fig.savefig()

    if kwargs.get('show', False):
        fig.show()

    return

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()

    parser.add_argument('traj-folder')
    parser.add_argument('--prefix', required=False, default='traj.xyz.{}')
    parser.add_argument('--plot-file', required=False, default=None)

    args = vars(parser.parse_args())
    main(**args)