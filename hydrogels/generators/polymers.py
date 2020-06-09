#!/usr/bin/env python
"""
Classes to make ReaDDy topologies that are polymers. A polymer is a chain
of monomers.
"""
import numpy as np 
from ..utils.topology import Topology

import starpolymers

class AbstractPolymer(Topology):
    """
    Wrapper for topology with basic Polymer operations
    that can be shared amongst many polymers.
    """
    def __init__(self, top_type : str, **kwargs):
        super().__init__(top_type, **kwargs)

class LinearPolymer(AbstractPolymer):
    """
    Linear Polymers are generated as a chain of atoms.
    """
    def __init__(
        self, 
        top_type : str, 
        n : int, 
        start : np.ndarray, 
        delta : np.ndarray,
        parameters = {'type' : 'homo'}
    ):

        super().__init__(
            top_type,
            sequence = self.generate_sequence(),
            positions = self.generate_positions()
        )

    def generate_sequence(self):
        return []
    
    def generate_positions(self):
        return []

    

    