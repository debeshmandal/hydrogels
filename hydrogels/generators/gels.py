#!/usr/bin/env python
"""
Gels are made of polymers. This package lives above polymers.py in the
molecule hierarchy.
"""
import numpy as np
from ..utils.system import System

class AbstractGel(System):
    """
    Initiators are systems of polymers and cross-linking agents that can be
    used to run simulations to form complete gels
    """
    def __init__(self):
        pass

    def add_polymers(self):
        return

    def add_reactions(self):
        return

class PDMS(AbstractGel):
    """
    PDMS gels are made of polymer chains covalently bonded
    to initiators that are cross-shaped with reaction sites 
    at each end of the 4 ends of the cross.
    """
    def __init__(self):
        pass

    def add_initiators(self, n_initiators):
        """
        An initiator is a readdy.TopologyRecord in the form of a
        branched polymer with n_arms = 4.
        """

        # molecule = .polymers.BranchedPolymer
        # use self.add_polymer method to add molecule to system aka self

        return
    
class Diacrylate(AbstractGel):
    """
    Diacrylate gels are made up of polymer chains where
    the polymer chains where the terminal ends are able to
    bond to each other.
    
    This means that all chains are identical and reactions
    can occur between the terminal ends of each chain.
    """
    def __init__(self):
        pass