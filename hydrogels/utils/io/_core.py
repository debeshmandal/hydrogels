import json

from typing import List, Tuple

import pandas as pd

from ..system import System
from ..topology import Topology

class CoreReader:
    def __init__(
        self, 
        particles: dict = None, 
        topologies: list = None, 
        metadata: dict = None
    ):
        if not particles:
            self._particles = {}

        if not topologies:
            self._topologies = []

        if not metadata:
            self.metadata = {}

    def add_particles(self, name, value):
        self._particles[name] = value

    @property
    def particles(self) -> dict:
        return self._particles

    def add_topology(
        self, 
        name, 
        sequence, 
        positions, 
        edges,
    ):
        topology = Topology(
            name, 
            sequence=sequence,
            positions=positions,
            edges=edges
        )
        self._topologies.append(topology)

    @property
    def topologies(self) -> List[Topology]:
        return self._topologies
    
    def system(self, **kwargs) -> System:
        if 'box' in self.metadata:
            system = System(self.metadata['box'])
        else:
            system = System(kwargs['box'])
        self.configure(system, **kwargs)
        return system
        
    def configure(
        self,
        system,
        diffusion_constant: float = None,
        diffusion_dictionary: float = None,
        bonding: dict = None,
    ):
        if diffusion_dictionary != None and diffusion_constant != None:
            raise ValueError('Please provide only one form for the diffusion constants!')

        metadata = self.metadata
        topologies = self.topologies
        particles = self.particles

        if diffusion_constant:
            diffusion = diffusion_constant
            for name, value in self.particles.items():
                system.insert_species(name, diffusion, value)
            
        elif diffusion_dictionary:
            diffusion = diffusion_dictionary
            for name, value in self.particles.items():
                system.insert_species(name, diffusion[name], value)
            
        for topology in self.topologies:
            if topology.top_type not in bonding:
                raise TypeError(
                    f'Topology ({topology.top_type}) has been found'
                    f' but no bonds can be found in the bonding dictionary:'
                    f'\n{json.dumps(bonding, indent=2)}'
                )
            settings = bonding[topology.top_type]
            topology.add_bond(**settings)
            system.insert_topology(
                topology, 
                diffusion_dictionary=diffusion_dictionary, 
                diffusion_constant=diffusion_constant
            )
        return