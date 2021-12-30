#!/usr/bin/env python
"""Container for enzyme dump files which outputs density_map
"""

import numpy as np
import pandas as pd

from utils import get_density, get_positions

from softnanotools.logger import Logger
logger = Logger('ENZYME')

class EnzymeContainer:
    def __init__(self, fname: str, bin_width: float = 1.0, box: float = 35.0, **kwargs):
        self.fname = fname
        self.positions = get_positions(self.fname)
        self.density_map = get_density(
            self.positions,
            bin_width,
            max_bin = box
        )

        logger.debug('Succesfully created EnzymeContainer!')

if __name__ == '__main__':
    enzymes = EnzymeContainer('dump/dump.enzyme.1000000.1')

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.plot(
        enzymes.density_map['r'], 
        enzymes.density_map['rho'], 
        'k-x'
    )
    fig.savefig('enzyme-test.png')


