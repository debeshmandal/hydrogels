#!/usr/bin/env python
"""
Gels systems containing of polymers. This package lives above polymers.py in the
molecule hierarchy.
"""
import random
from itertools import product

import pandas as pd
import numpy as np
from scipy.spatial.distance import pdist, squareform

from ...utils.topology import Topology
from ..polymers import LinearPolymer, CrosslinkingPolymer

class Gel(Topology):
    """
    A Gel is a ReaDDy Topology that can be used
    to generate systems to model hydrogels.
    """
    def __init__(
        self,
        top_type,
        positions: np.ndarray = None,
        monomer: str = 'monomer',
        unbonded: str = 'unbonded',
    ):

        self.monomer = monomer
        self.unbonded = unbonded

        if isinstance(positions, (np.ndarray, list, tuple)):
            super().__init__(
                top_type,
                positions=positions,
                sequence=len(positions) * [monomer],
                names=[self.monomer, self.unbonded]
            )

        else:
            super().__init__(top_type)

    def configure_bonds(self, kind, **kwargs):

        # configure normal bond like normal
        self.add_bond(kind, self.monomer, self.monomer, **kwargs)

        # set force constant to zero for unbonded topology particles
        ghost_bond = {
            'force_constant': 0.0,
            'length': 1.0
        }
        self.add_bond('harmonic', self.monomer, self.unbonded, **ghost_bond)
        self.add_bond('harmonic', self.unbonded, self.unbonded, **ghost_bond)
        return

