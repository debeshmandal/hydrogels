#!/usr/bin/env python
"""
Gels systems containing of polymers. This package lives above polymers.py in the
molecule hierarchy.
"""
import numpy as np
from ..utils.system import System
from polymers import LinearPolymer, CrosslinkingPolymer

class AbstractGel(System):
    """
    Initiators are systems of polymers and cross-linking agents that can be
    used to run simulations to form complete gels
    """
    def __init__(self):
        pass

    def add_polymers(self, polymer_list):
        return

    def add_reactions(self):
        return

class PDMS(AbstractGel):
    """
    PDMS gels are made of polymer chains covalently bonded
    to initiators that are cross-shaped with reaction sites 
    at each end of the 4 ends of the cross.
    """
    def __init__(
        self, 
        n_crosslinkers : int = 3, 
        n_polymers : int = 10, 
        kap_crosslinker : int = 4, 
        lam_crosslinker : int = 4,
        lam_polymer : int = 20
    ):
        self.generate_topologies()

    def crosslinker(self, start : np.ndarray, a1 : np.ndarray) -> CrosslinkingPolymer:
        molecule = CrosslinkingPolymer(
                'crosslinker', 
                self.kap_crosslinker,
                self.lam_crosslinker,
                start
            )
        return molecule

    def polymer(self, start : np.ndarray, a1 : np.ndarray) -> LinearPolymer:
        molecule = LinearPolymer(
                'polymer', 
                self.lam_polymer,
                start
            )
        return
    
    def generate_topologies(self):
        return

    def _add_crosslinkers(self):
        """
        An initiator is a readdy.TopologyRecord in the form of a
        branched polymer with n_arms = 4.
        """

        # molecule = .polymers.BranchedPolymer
        # use self.add_polymer method to add molecule to system aka self

        for i in range(self.n_crosslinkers):
            start_pos = np.array([0., 0., 0.])
            direction = np.array([1., 0., 0.])
            mol = self.crosslinker(start_pos, direction)
            self._topologies.append(mol)

    def _add_polymers(self):
        """
        An initiator is a readdy.TopologyRecord in the form of a
        branched polymer with n_arms = 4.
        """
        for i in range(self.n_polymers):
            start_pos = np.array([0., 0., 0.])
            direction = np.array([1., 0., 0.])
            mol = self.crosslinker(start_pos, direction)
            self._topologies.append(mol)
    
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