#!/usr/bin/env python
"""Takes a set of gel dump files and calculates the volume
using convex hull algorithms"""

import numpy as np
import pandas as pd

from scipy.spatial import ConvexHull
from scipy.spatial.distance import pdist

from potential import Calculation
from utils import get_density, get_positions

from softnanotools.logger import Logger
logger = Logger('MICROGEL')

class Microgel(ConvexHull):
    def __init__(
        self, fname: str, 
        bin_width: float = 1.0, 
        potential_settings: dict = {}, 
        box: float = 35.0,
        **kwargs
    ):
        self.fname = fname
        self.positions = get_positions(self.fname)
        super().__init__(self.positions, **kwargs)

        self.density_map = get_density(self.positions, bin_width, max_bin=box)

        self.density = len(self.positions) / self.volume

        self._dist = pdist(self.positions)
        self._dist.sort()
        
        self.radius = ((3 * self.volume / (4 * np.pi))) ** (1./3.)

        self.potential = Calculation(
            self.fname, 
            box = max(self.density_map['r']),
            dr=bin_width,
            **potential_settings
        )

        self.energy_map = self.potential.potential(**potential_settings['parameters'])
        logger.debug('Successfully setup Microgel object')

if __name__ == '__main__':
    hull = Microgel('dump/dump.gel.10000000')
    logger.info(f'Volume: {hull.volume:.3f} '
        f'[R={((3 * hull.volume / (4 * np.pi))) ** (1./3.):.3f}]')
    logger.info(f'Surface Area: {hull.area:.3f} '
        f'[R={((hull.area / (4 * np.pi))) ** (1./2.):.3f}]')
    logger.info(f'Radius (3V/A): {3 * hull.volume / hull.area:.3f}')
    logger.info(f"Radius (max): {hull._radius:.3f} [std={hull._radius_err:.3f}]")
    logger.info(f'Density: {hull.density:.3f}')
    
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(2, sharex=True)
    ax[0].plot(hull.density_map['r'], hull.density_map['rho'], 'k-x')
    ax[0].plot(
        [min(hull.density_map['r']), max(hull.density_map['r'])],
        [hull.density, hull.density],
        'k:'
    )
    ax[0].plot(
        [hull._radius, hull._radius],
        [min(hull.density_map['rho']), max(hull.density_map['rho'])],
        'r:',
        label='Top N distances'
    )
    ax[0].plot(
        [3 * hull.volume / hull.area, 3 * hull.volume / hull.area],
        [min(hull.density_map['rho']), max(hull.density_map['rho'])],
        'g:',
        label='3V/A'
    )
    ax[0].plot(
        [((3 * hull.volume / (4 * np.pi))) ** (1./3.), ((3 * hull.volume / (4 * np.pi))) ** (1./3.)],
        [min(hull.density_map['rho']), max(hull.density_map['rho'])],
        'm:',
        label='(3V/4pi)^(1/3)'
    )
    ax[0].plot(
        [((hull.area / (4 * np.pi))) ** (1./2.), ((hull.area / (4 * np.pi))) ** (1./2.)],
        [min(hull.density_map['rho']), max(hull.density_map['rho'])],
        'b:',
        label='(A/4pi)^(1/2)'
    )
    ax[0].legend()

    energy = hull.potential.potential(
        sig=1.0,
        eps=1.0,
        cutoff=2 ** (1./6.),
        shifted=True,
        max_energy=5.
    )

    logger.debug(f"Energy:\n{energy}")
    ax[1].errorbar(
        energy['r'],
        energy['mean'],
        yerr=energy['std'],
        fmt='kx-',
        capsize=5
    )

    energy = hull.potential.potential(
        sig=1.0,
        eps=1.0,
        cutoff=2.5,
        max_energy=5.
    )

    logger.debug(f"Energy:\n{energy}")
    ax[1].errorbar(
        energy['r'],
        energy['mean'],
        yerr=energy['std'],
        fmt='bo-',
        capsize=5
    )

    fig.savefig('hull-density.png')
