"""A system that runs the enzymatic degradation reactions
"""
import numpy as np

from .. import System, Topology
from ..generators.gels import Gel

class EnzymaticDegradation(System):
    def __init__(
        self, 
        box: list, 
        topologies, 
        released: str = 'released',
        decay_rate: float = 1e-3,
        **kwargs
    ):
        super().__init__(box)
        self.settings = kwargs
        self.decay_rate = kwargs.get('decay_rate', 1e-3)

        # managed the released species that has no particles yet
        self.released = released
        self.insert_species(released, self.settings.get('diffusion_constant', 1.0), [])

        # manage topologies
        if isinstance(topologies, Topology):
            topologies = [topologies]
        for top in topologies:
            self.insert_topology(top, diffusion_constant=self.settings.get('diffusion_constant', 1.0))
            if isinstance(top, Gel):
                top.register_decay(self, released=self.released, rate=self.decay_rate)
        
        # add lj potential for everything
        self.manager.add('lj', 'all', 'all', **self.settings)

    def add_enzyme(self, positions, name: str = 'enzyme', rate: float=1e-3, radius: float=2.0, diffusion_constant: float = None):
        if diffusion_constant == None:
            diffusion_constant = self.settings.get('diffusion_constant', 1.0)
        self.insert_species(name, diffusion_constant, positions)
        self.manager.add('lj', name, 'all', **self.settings)

        for top in self._topologies:
            top.register_degradation(self, name, rate, radius)
        return

    def add_payload(self, positions: np.ndarray, name: str = 'payload', diffusion_constant: float = None):
        if diffusion_constant == None:
            diffusion_constant = self.settings.get('diffusion_constant', 1.0)
        self.insert_species(name, diffusion_constant, positions)
        self.manager.add('lj', name, 'all', **self.settings)
        return