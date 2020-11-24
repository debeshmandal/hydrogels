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
        positions: np.ndarray,
        monomer: str = 'monomer',
        bonded: str = 'bonded',
    ):
        super().__init__(top_type, *args, **kwargs)
        self.names = [monomer, bonded]

    def configure_bonds(self, kind, **kwargs):
        self.add_bond(kind, self.monomer, self.monomer, **kwargs)
        self.add_bond(kind, self.monomer, self.bonded, **kwargs)
        self.add_bond(kind, self.bonded, self.bonded, **kwargs)
        return

    def configure_potentials(self):
        return

