import numpy as np

from .core import Gel

class LennardJonesGel(Gel):
    """
    A Lennard-Jones Gel is a gel with a given volume, number and 
    hence number density that is composed of lennard-jones particles
    where the k-nearest neighbours are bonded.
    """
    def __init__(
            self,
            bonded = 'bonded',
            unbonded = 'unbonded',
            topology_type = 'gel',
            **kwargs
        ):
        self.top_type = top_type
        self.monomer = monomer
        self.unbonded = unbonded
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