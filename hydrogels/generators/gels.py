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
            spacing: float = None,
            k : int = 6,
            top_type : str = 'lj-gel',
            monomer : str = 'monomer',
            unbonded : str = 'unbonded',
            **kwargs
        ):
        self.top_type = top_type
        self.monomer = monomer
        self.unbonded = unbonded
        self.initialise_geometry(N, V, nV, R, spacing)
        super().__init__(box)
        self._species += [self.monomer, self.unbonded]

        self.add_topology_species(monomer, kwargs['diffusion_constant'])
        self.add_topology_species(unbonded, kwargs['diffusion_constant'])
        self.topologies.add_type(top_type)
        self.topologies.configure_harmonic_bond(
                monomer, 
                monomer, 
                force_constant = kwargs['bond_strength'],
                length = kwargs.get('bond_length', self.spacing)
            )

        _sig = kwargs.get('lj_sig', self.spacing)
        self.potentials.add_lennard_jones(
                monomer, 
                monomer,
                m=12,
                n=6,
                shift=True,
                epsilon = kwargs['lj_eps'],
                sigma = _sig,
                cutoff = kwargs.get('lj_cutoff', 2.5 * _sig)
            )

    def initialise_geometry(self, N, V, nV, R, spacing):

        # We only want one out of spacing and nV
        if spacing != None and nV != None:
            raise ValueError('Only provide one of either spacing and nV')
        elif nV:
            # set spacing here, and have nV property later
            self.spacing = nV ** -0.357
        elif spacing:
            nV = spacing ** -2.8
            self.spacing = spacing
        
        density_checker = True if (spacing or nV) else False


        # Check that only one of R and V are provided and create
        # boolean to store this information
        if R != None and V != None:
            raise ValueError('Only provide one of either R and V')
        if R:
            self.radius = R
        elif V:
            self.radius = np.cbrt(0.75 * (1./np.pi) * V)

        geometry_checker = True if (R or V) else False

        if density_checker and geometry_checker:
            # radius and spacing have been calculated
            pass
        elif N:
            if not density_checker:
                self.spacing = self._get_spacing(N)
            elif not geometry_checker:
                self.radius = self._get_radius(N)
            else:
                raise TypeError('You have not provided [R|V] or [spacing|nV]')
        else:
            raise TypeError('Since you have not provided [R|V] and [spacing|nV], you must provide N')

        if self.spacing < 0.0:
            raise ValueError(
                f'Increase the density (i.e. N) because the model only '
                f'works for high density systems and N is currently {N} which '
                f'means that the spacing is {self.spacing}!'
            )
        
        # generate positions
        self.positions = self.generate_positions()

    def _get_radius(self, N: int) -> float:
        _volume = float(N) / (self.spacing ** -2.8)
        _radius = np.cbrt(0.75 * (1./np.pi) * _volume)
        return _radius

    def _get_spacing(self, N: int) -> float:
        _nV = N / self.volume
        _spacing = _nV ** -0.357
        return _spacing

    @property
    def N(self) -> float:
        return len(self.positions)

    @property
    def nV(self) -> float:
        return self.N / self.volume

    @property
    def volume(self) -> float:
        return 4./3. * np.pi * self.radius ** 3

    def generate_positions(self) -> np.ndarray:
        """
        Generate positions within a sphere
        """
        n_gridpoints = int((self.radius * 2.) / self.spacing) + 1
        positions = pd.DataFrame(
            np.array(
                [
                    [i, j, k] for i, j, k in \
                        product(
                            range(n_gridpoints), 
                            range(n_gridpoints), 
                            range(n_gridpoints)
                        )
                ]
            ) * self.spacing - self.radius
        ).rename(columns={
            0: 'x',
            1: 'y',
            2: 'z',
        })
        print(self.spacing, self.radius, n_gridpoints)
        print(positions)
        
        positions = positions[
            np.sqrt(
                positions['x'] ** 2 \
                + positions['y'] ** 2 \
                + positions['z'] ** 2
            ) <= self.radius + self.spacing / 2
        ].reset_index(drop=True)
        return positions.values

    def generate_edges(self, positions, n=6) -> np.ndarray:
        """Create bonding topology for gel object"""
        # create dataframe of indices sorted by distance
        pairs = np.argsort(
            pd.DataFrame(
                squareform(pdist(positions))
            )
        ).iloc[:, 1 : 1+n]

        # create nested list of pairs
        result = []
        for idx in pairs.index:
            for pair in pairs.loc[idx]:
                result.append([idx, pair])

        # return as array
        return np.array(result)

    def initialise_simulation(self, **kwargs):
        simulation = super().initialise_simulation(**kwargs)
        topology = simulation.add_topology(
            self.top_type,
            len(self.positions) * [self.monomer],
            self.positions
        )
        self._topologies.append('Manual Topology LJ')
        for atoms in self.generate_edges(self.positions):
            topology.get_graph().add_edge(atoms[0], atoms[1])

        for species, positions in self._particles.items():
            simulation.add_particles(species, positions)
        return simulation

    # to set up simulation:
    # add LJ potential for six potentials types - enzyme, bonded, unbonded combos
    # add reaction that when an enzyme encounters a gel particle, it changes from bonded to unbonded
    # and its epsilon is set to zero and sigma set so that it is purely repulsive

