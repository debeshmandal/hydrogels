#!/usr/bin/env python
"""Service for calculating the radial potential generated by the 
microgel"""

from typing import List
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.spatial.distance import cdist

from tqdm import tqdm

from softnanotools.logger import Logger
logger = Logger('POTENTIAL')

def import_particles(fname: str) -> pd.DataFrame:
    """Import particles from LAMMPS dump file"""

    logger.debug(f'Reading files from {fname}')
    particles = pd.read_csv(
        fname,
        delim_whitespace=True,
        skiprows=9,
        header=None,
        names=['x', 'y', 'z']
    )
    return particles

def generate_mesh(samples_per_shell: float, dr: float, max_distance) -> List[np.ndarray]:
    """Creates a fibonacci spheres with `sample_per_shell` points on their
    surface, ranging from distances `dr` to `max_distance` in multiples of
    `dr`.

    The result is nested in a MxNx3 array where N is `samples_per_shell` and 
    M is approximately `max_distance`/`dr`

    Each layer (i.e. each Nx3 array) has columns r, theta, phi
    """
    
    # initialise empty list
    array_list = []

    # get number of shells
    N_shells = int(max_distance / dr)
    logger.debug(f'Creating {N_shells} fibonacci spheres with a spacing {dr}')

    for i in range(N_shells):

        # create indices and empty results array
        indices = np.arange(0, samples_per_shell, dtype=float) + 0.5
        array = np.zeros((samples_per_shell, 3))

        # get r
        array[:, 0] = dr * (i + 1)

        # get theta
        array[:, 1] = np.pi * (1 + 5 ** 0.5) * indices

        # get phi
        array[:, 2] = np.arccos(1 - 2 * indices / samples_per_shell)

        # add to results list
        array_list.append(array)

    logger.debug(
        f'Generate Mesh with spherical co-ordinate:\n{pd.DataFrame(array_list[0])}'
    )

    return array_list

def spherical_to_xyz(array: np.ndarray) -> np.ndarray:
    """Takes an Nx3 array with columns r->theta->phi and returns 
    an XYZ array"""

    # check dimensionality is correct
    assert array.shape[1] == 3

    # initialise empty array
    result = np.zeros(array.shape)

    # do calculation without r

    # x-> y-> z         r              theta                 phi
    result[:, 0] = array[:, 0] * np.sin(array[:, 1]) * np.cos(array[:, 2])
    result[:, 1] = array[:, 0] * np.sin(array[:, 1]) * np.sin(array[:, 2])
    result[:, 2] = array[:, 0] * np.cos(array[:, 1])

    return result

def lennard_jones(
    r: np.ndarray, 
    sig: float = 1.0, 
    eps: float = 1.0, 
    cutoff: float = 1.122,
    shifted: bool = False,
) -> np.ndarray:
    """Returns Lennard-Jones 12-6 potential
    """
    # calculate inside brackets
    result =  (sig/r) ** 12 - (sig/r) ** 6

    # account for shift
    if shifted:
        result += eps

    # multiply by 4 epsilon
    result = result * 4 * eps

    # apply cutoff
    result[r > cutoff] = 0

    return result


class Calculation:
    """Object for storing a single gel-mesh combination for
    calculating a discrete potential summation
    """
    def __init__(
        self, 
        fname: str, 
        box: float = 30.0, 
        dr: float = 0.5, 
        samples_per_shell: int = 100, 
        kind: str = 'lennard_jones',
        max_energy: float = 2.5,
        **kwargs,
    ):
        self.fname = fname
        self.positions = import_particles(fname)
        self.mesh = generate_mesh(samples_per_shell, dr, box)

        # get bin position from self.positions
        self.bins = [
            r[0][0] for r in self.mesh
        ]

        self.kind = kind
        self.max_energy = max_energy

        potentials = {
            'lennard_jones': lennard_jones
        }

        self.function = potentials[kind]

        logger.debug('Successfully initialised Calculation instance')

    def potential(
        self,
        beta: float = 1.0, 
        **parameters
    ) -> pd.DataFrame:
        """Calculates the actual potential, returning a dataframe
        containing the mean and standard deviation values from
        a single configuration"""

        # get distances between each point in the mesh 
        # and each particle - this would have dimensions:

        # N x M where N is the number of particles and M is the 
        # number of mesh points

        # this means it scales linearly with the number of particles
        # (phew!) and cubicly with the box size/delta - but this is constant
        # between different microgels
        positions = self.positions[['x', 'y', 'z']].to_numpy()

        # initialise results list using centre point
        r = []

        # filter out stupidly large values
        #pot = potential(np.linalg.norm(positions, axis=1))
        #pot[pot > max_energy] = 0
        mean = []

        # std is 0 since there 
        std = []
        raw = []

        #logger.info(
        #    'Successfully initialised results lists for potential calculation:'
        #    f'\n\tr={r[0]}\tmean={mean[0]:.3f}\tstd={std[0]}\traw={raw[0]}'
        #)
        
        for i, layer in enumerate(self.mesh):

            # get distance
            distances = cdist(positions, spherical_to_xyz(layer))
            if i == 0:
                logger.debug(f'First Iteration `distances` shape: {distances.shape}')

            # calculate the energy vector
            energy = self.function(distances, **parameters)

            # filter energy to remove
            #energy[energy > self.max_energy] = np.mean(energy[energy < self.max_energy])

            energy = energy * np.exp(-beta * energy)

            
            if i == 0:
                logger.debug(f'First Iteration `energy` shape: {energy.shape}')

            energy = np.sum(energy, axis=1)
            if i == 0:
                logger.debug(f'First Iteration `energy` shape after summation: {energy.shape}')

            # append results to results lists
            r.append(self.bins[i])
            mean.append(np.mean(energy))
            std.append(np.std(energy))
            raw.append(energy)

        # create dataframe
        results = pd.DataFrame({
            'r': r,
            'raw': raw,
            'mean': mean,
            'std': std,
        })

        return results

def main(
    fnames: List[str],
    dr: float = 1.0,
    box: float = 35.0,
    samples_per_shell = 50,
    **params
):
    final = pd.DataFrame()
    # create instance
    for i, fname in enumerate(tqdm(fnames)):
        calc = Calculation(fname, dr=dr, box=box, samples_per_shell=samples_per_shell)
        pot = calc.potential(**params)
        if i == 0:
            final['r'] = pot['r']
            if isinstance(pot['raw'], type(None)): 
                continue
            final['raw'] = pot['raw']

        else:
            if isinstance(pot['raw'], type(None)): 
                continue
            final['raw'].append(pot['raw'])

    final['mean'] = final['raw'].apply(lambda x: np.mean(x))
    final['std'] = final['raw'].apply(lambda x: np.std(x))

    return final

if __name__ == '__main__':
    from density import calculate_density

    fig, ax = plt.subplots(2, sharex=True)

    density = calculate_density()

    ax[0].errorbar(
        density['r'], 
        density['mean'], 
        yerr=density['std'], 
        fmt='k-x'
    )

    ax[0].set_ylabel('density')

    for sig in [0.5, 1.0, 2.0]:
        final = main(Path('dump').glob('dump.*'), cutoff=2.5, sig=sig)
        ax[1].errorbar(
            final['r'], 
            final['mean'], 
            yerr=final['std'], 
            fmt='x-', 
            capsize=5.0, 
            label=f'epsilon={sig}'
        )
        
    ax[1].legend()
    ax[1].set_ylabel('U(r)')
    ax[1].set_xlabel('r')
    plt.savefig('potential-sum.png')