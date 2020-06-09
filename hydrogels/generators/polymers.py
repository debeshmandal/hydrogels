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
        start : np.ndarray = np.array([[0., 0., 0.]])
    ):

        super().__init__(
            top_type,
            sequence = self.generate_sequence(n),
            positions = self.generate_positions(n, start)
        )

    def generate_sequence(self, n):
        return ['test'] * n
    
    def generate_positions(self, length, start):
        # use starpolymers to generate positions
        positions = \
            starpolymers.molecules.LinearPolyelectrolyte(
                {
                    'lam' : length, 
                    'charge' : { 'max' : 0 }
                }
            )._atoms
        positions = positions[['x', 'y', 'z']].values
        positions[:, 0] += start[:, 0]
        positions[:, 1] += start[:, 1]
        positions[:, 2] += start[:, 2]
        return positions

class CrosslinkingPolymer(AbstractPolymer):
    """
    Linear Polymers are generated as a chain of atoms.
    """
    def __init__(
        self, 
        top_type : str, 
        kap : int,
        lam : int,
        start : np.ndarray = np.array([[0., 0., 0.]])
    ):

        super().__init__(
            top_type,
            sequence = self.generate_sequence(kap, lam),
            positions = self.generate_positions(kap, lam, start)
        )

    def generate_sequence(self, kap, lam):
        return ['test'] * (kap * lam + 1)
    
    def generate_positions(self, kap, lam, start):
        # use starpolymers to generate positions
        positions = \
            starpolymers.molecules.StarPolyelectrolyte(
                {
                    'kap' : kap,
                    'lam' : lam, 
                    'charge' : { 'max' : 0 }
                }
            )._atoms
        positions = positions[['x', 'y', 'z']].values
        positions[:, 0] += start[:, 0]
        positions[:, 1] += start[:, 1]
        positions[:, 2] += start[:, 2]
        return positions
    

    