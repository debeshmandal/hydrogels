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
        species: list = None, 
        topology_species: list = None, 
        topologies: list = None, 
        *args, 
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        # record and register all species, topology_species and topologies
        if species:
            self._species += species
        if topology_species:
            self._topology_species += topology_species
        if topologies:
            self._topologies += topology_species
            
        self._particles = {} # positions
        self._bonds = pd.DataFrame() # edges
        self._pairs = pd.DataFrame() # pair potentials
