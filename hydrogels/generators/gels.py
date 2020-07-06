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

    def add_polymers(self, atom_shift=0):
        # access self._topologies 

        # for each polymer, 
        
        # add positions and sequence to the system

        # add edges but remember to do + atom_shift and after this update the atom_shift

        return

    def add_reactions(self):

        return

    def add_potentials(self):

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

class LennardJonesGel(AbstractGel):
    """
    A Lennard-Jones Gel is a gel with a given volume, number and 
    hence number density that is composed of lennard-jones particles
    where the k-nearest neighbours are bonded.
    """
    def __init__(
            self, 
            N : int = None, 
            V : float = None, 
            nV : float = None,
            R : float = None,
            k : int = 4
        ):
        self.deduce_geometry(N, V, nV, R)

    def deduce_geometry(self, N, V, nV, R):

        # Check that only one of R and V are provided and create
        # boolean to store this information
        if R != None and V != None:
            raise ValueError('Only provide one of either R and V')
        geom_checker = False if nV == None and R == None else True

        # At least two of the list must be True
        checker_list = [N, nV, geom_checker]
        if checker_list.count(None) > 1:
            raise ValueError('Check which arguments have been passed')

        # We only need the radius and the N, the rest of the value
        # are stored as properties
        self.radius = R if R != None else self._get_radius(N, V, nV)
        self.N = N if N != None else self._get_N(nV)

    def _get_radius(self, N : int, V : float, nV : float) -> float:
        if V == None:
            try:
                V = N / nV
            except TypeError as e:
                raise e('N and nV must be provided if either R or V are not.')
        radius = np.cbrt(0.75 * (1./np.pi) * V)
        return radius

    def _get_N(self, nV : float) -> int:
        if nV == None:
            raise ValueError('nV must be provided if N is not')
        N = int(nV * self.volume)
        return N

    @property
    def concentration(self) -> float:
        return self.N / self.volume

    @property
    def volume(self) -> float:
        return 4./3. * np.pi * self.radius ** 3

    def generate_positions(self) -> np.ndarray:
        """
        Generate positions within a sphere
        """
        V = []
        costheta = []
        phi = []
        for i in range(self.N):
            V.append(random.uniform(0., self.volume))
            costheta.append(random.uniform(-1., 1.))
            phi.append(random.uniform(0., 2*np.pi))
        R = np.cbrt(np.array(V))
        theta = np.arccos(costheta)
        array = np.ones((N, 3))
        array[:, 0] = R * np.sin(theta) * np.cos(phi)
        array[:, 1] = R * np.sin(theta) * np.sin(phi)
        array[:, 2] = R * np.cos(theta)
        return array

    def generate_edges(self) -> tuple:
        return

    # to set up simulation:
    # add LJ potential for six potentials types - enzyme, bonded, unbonded combos
    # add reaction that when an enzyme encounters a gel particle, it changes from bonded to unbonded
    # and its epsilon is set to zero and sigma set so that it is purely repulsive

