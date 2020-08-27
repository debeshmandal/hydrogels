#!/usr/bin/env python
"""
Gels systems containing of polymers. This package lives above polymers.py in the
molecule hierarchy.
"""
import random

import numpy as np
from scipy.spatial.distance import pdist, squareform

from ..utils.system import System
from .polymers import LinearPolymer, CrosslinkingPolymer


class AbstractGel(System):
    """
    Initiators are systems of polymers and cross-linking agents that can be
    used to run simulations to form complete gels
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._particles = {}

    def add_enzyme(
            self,
            positions,
            species='enzyme', 
            reaction: str = None,
            spatial_reaction : str = None,
            rate : float = None,
            radius : float = None,
            diffusion_constant : float = 1.0,
            **kwargs
        ):
            if species not in self._species: 
                self.add_species(species, diffusion_constant)
                self._species.append(species)

            for name in self._species:
                self.potentials.add_lennard_jones(species, name, **kwargs)
            
            if reaction:
                self.reactions.add(reaction, rate=rate, radius=radius)
            
            if spatial_reaction:
                self.topologies.add_spatial_reaction(spatial_reaction, rate=rate, radius=radius)
                
            self._particles[species] = positions
        

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
            box : np.array,
            N : int = None, 
            V : float = None, 
            nV : float = None,
            R : float = None,
            k : int = 4,
            top_type : str = 'lj-gel',
            monomer : str = 'monomer',
            unbonded : str = 'unbonded',
            **kwargs
        ):
        self.top_type = top_type
        self.monomer = monomer
        self.unbonded = unbonded
        self.initialise_geometry(N, V, nV, R)
        super().__init__(box)
        self._species += [self.monomer, self.unbonded]

        self.add_topology_species(monomer, kwargs['diffusion_constant'])
        self.add_topology_species(unbonded, kwargs['diffusion_constant'])
        self.topologies.add_type(top_type)
        self.topologies.configure_harmonic_bond(
                monomer, 
                monomer, 
                force_constant = kwargs['bond_strength'],
                length = kwargs['bond_length']
            )

        self.potentials.add_lennard_jones(
                monomer, 
                monomer,
                m=12,
                n=6,
                shift=True,
                epsilon = kwargs['lj_eps'],
                sigma = kwargs['lj_sig'],
                cutoff = kwargs['lj_cutoff']
            )

    def initialise_geometry(self, N, V, nV, R):

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
        array = np.ones((self.N, 3))
        array[:, 0] = R * np.sin(theta) * np.cos(phi)
        array[:, 1] = R * np.sin(theta) * np.sin(phi)
        array[:, 2] = R * np.cos(theta)
        return array

    def generate_edges(self, positions, n=4) -> np.ndarray:
        idxs = np.argsort(squareform(pdist(positions)))[:, 1:]
        cxns = np.zeros((len(idxs), len(idxs)), dtype=int)
        for i, row in enumerate(idxs):
            for j, idx in enumerate(row):
                if cxns[i, :].sum() >= n: break
                if cxns[:, idx].sum() >= n: 
                    continue
                elif cxns[i, idx] != 1 and cxns[idx, i] != 1:
                    cxns[i, idx] += 1
                    cxns[idx, i] += 1
        result = []
        for i in range(cxns.shape[0]):
            for j in range(i):
                if cxns[i][j]:
                    result.append([i, j])
        return result

    def initialise_simulation(self, **kwargs):
        simulation = super().initialise_simulation(**kwargs)
        positions = self.generate_positions()
        topology = simulation.add_topology(
            self.top_type,
            len(positions) * [self.monomer],
            positions
        )
        self._topologies.append('Manual Topology LJ')
        for atoms in self.generate_edges(positions):
            topology.get_graph().add_edge(atoms[0], atoms[1])

        for species, positions in self._particles.items():
            simulation.add_particles(species, positions)
        return simulation

    # to set up simulation:
    # add LJ potential for six potentials types - enzyme, bonded, unbonded combos
    # add reaction that when an enzyme encounters a gel particle, it changes from bonded to unbonded
    # and its epsilon is set to zero and sigma set so that it is purely repulsive

