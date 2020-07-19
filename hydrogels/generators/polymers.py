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
        self.start = kwargs.get('start', np.array([[0., 0., 0.]]))
        super().__init__(top_type, **kwargs)

    @property
    def positions(self) -> np.ndarray:
        # use starpolymers to generate positions
        _positions = self.molecule._atoms
        _positions = _positions[['x', 'y', 'z']].values
        _positions[:, 0] += self.start[:, 0]
        _positions[:, 1] += self.start[:, 1]
        _positions[:, 2] += self.start[:, 2]
        return _positions

    @property
    def edges(self) -> tuple:
        _edges = self.molecule._bonds[['atom_1', 'atom_2']].values - 1
        return _edges


class LinearPolymer(AbstractPolymer):
    """
    Linear Polymers are generated as a chain of atoms.
    """
    def __init__(
        self, 
        top_type : str, 
        n : int,
        **kwargs
    ):
        self.n = n
        #self.start = kwargs.get('start', np.array([0., 0., 0.]))
        super().__init__(
            top_type,
            sequence = self.generate_sequence(kwargs=kwargs),
        )

    def generate_sequence(self, **kwargs):
        sequence = kwargs.get('sequence', None)
        head = kwargs.get('head_name', 'head')
        core = kwargs.get('core_name', 'core')
        if sequence == None:
            return [head] + [core] * (self.n-2) + [head]
        else:
            return sequence

    @property
    def molecule(self):
        mol = starpolymers.molecules.LinearPolyelectrolyte(
                {
                    'lam' : self.n,
                    'charge' : { 'max' : 0 }
                }
            )
        return mol

class CrosslinkingPolymer(AbstractPolymer):
    """
    Linear Polymers are generated as a chain of atoms.
    """
    def __init__(
        self, 
        top_type : str, 
        kap : int,
        lam : int,
        **kwargs
    ):
        self.kap = kap
        self.lam = lam
        
        super().__init__(
            top_type,
            sequence = self.generate_sequence(kwargs=kwargs),
        )

    def generate_sequence(self, **kwargs):
        sequence = kwargs.get('sequence', None)
        head = kwargs.get('head_name', 'head')
        core = kwargs.get('core_name', 'core')
        if sequence == None:
            return ([head] + (self.lam-1) * [core]) * self.kap + [core]
        else:
            return sequence

    @property
    def molecule(self):
        mol = starpolymers.molecules.StarPolyelectrolyte(
                {
                    'kap' : self.kap,
                    'lam' : self.lam, 
                    'charge' : { 'max' : 0 }
                }
            )
        return mol
    

    