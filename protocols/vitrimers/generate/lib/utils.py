import numpy as np
import pandas as pd

from softnanotools.logger import Logger
logger = Logger('UTILS')

def get_positions(fname: str) -> np.ndarray:
    """Takes LAMMPS dump file and returns the positions
    in an Nx3 array
    """
    logger.info(f'Reading positions from {fname}')

    # read file to figure out how many rows to skip
    skip = -1
    with open(fname, 'r') as f:
        for i, line in enumerate(f.readlines()):
            if line.startswith('ITEM: ATOMS'):
                logger.debug(f'Rows to skip = {i}')
                skip = i
                break

    # make sure skip has been assigned since it should never be -1
    assert skip != -1

    data = pd.read_csv(
        fname,
        delim_whitespace=True,
        header=None,
        skiprows=i+1
    )

    logger.debug(f'Got positions:\n{data}')

    positions = data.to_numpy()
    return positions

def get_density(
    positions: np.ndarray, 
    bin_width: float = 1.0,
    max_bin: float = None,
) -> pd.DataFrame:
    """Takes an array positions and returns the radial density
    as a function from the point [0, 0, 0]

    The bin_width can be provided and the limits are [0, max_bin], 
    where max_bin = 1.25 * max_distance within the distance array.

    Returns a Dataframe with columns 'r', and 'rho'    
    """
    # get distances
    distances = np.linalg.norm(positions, axis=1)

    # make histogram
    if not max_bin:
        max_bin = 1.25 * max(distances)
    bins = np.arange(bin_width, max_bin + bin_width, bin_width)
    histogram = np.histogram(distances, bins=bins)

    # create dataframe
    data = pd.DataFrame()
    data['r'] = histogram[1][:-1]
    data['rho'] = histogram[0] / (4 * np.pi * data['r'] ** 2 * bin_width)

    return data