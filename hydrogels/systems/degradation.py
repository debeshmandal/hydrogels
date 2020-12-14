"""A system that runs the enzymatic degradation reactions
"""
import numpy as np

from softnanotools.logger import Logger
logger = Logger(__name__)

from .. import System, Topology
from ..generators.gels import Gel

class EnzymaticDegradation(System):
    def __init__(
        self, 
        box: list,
        released: str = 'released',
        decay_rate: float = 1e-3,
        diffusion_constant: float = None,
        diffusion_dictionary: dict = None,
        epsilon: float = 0.0,
        sigma: float = 1.0,
        cutoff: float = 1.0,
        **kwargs
    ):
        super().__init__(box)
        self._kwargs = {
            'epsilon' : epsilon,
            'sigma' : sigma,
            'cutoff' : cutoff,
            **kwargs
        }
        self.decay_rate = decay_rate

        # managed the released species that has no particles yet
        self.released = released
        if diffusion_constant:
            self.insert_species(
                released, 
                diffusion_constant,
                []
            )
        elif diffusion_dictionary:
            self.insert_species(
                released, 
                diffusion_dictionary[released],
                []
            )
        else:
            logger.error('Please provide either a diffusion dictionary or diffusion constant')

        self.diffusion_constant = diffusion_constant
        self.diffusion_dictionary = diffusion_dictionary

        # add lj potential for everything
        #self.manager.add('lj', 'all', 'all', **self.settings)

    def register_gels(self):
        # manage topologies
        for top in self.topology_list:
            if isinstance(top, Gel):
                top.register_decay(self, released=self.released, rate=self.decay_rate)

    def add_enzyme(self, positions, name: str = 'enzyme', rate: float=1e-3, radius: float=2.0, diffusion_constant: float = None, potentials: bool = False):
        if diffusion_constant == None:
            if self.diffusion_constant != None:
                diffusion_constant = self.diffusion_constant
            elif self.diffusion_dictionary != None:
                diffusion_constant = self.diffusion_dictionary[name]
            else:
                logger.error(f'No diffusion constant provided for {name}!')
        self.insert_species(name, diffusion_constant, positions)
        if potentials:
            self.manager.add('lj', name, 'all', **self._kwargs)

        for top in self._topologies:
            top.register_degradation(self, name, rate, radius)
        return

    def add_payload(self, positions: np.ndarray, name: str = 'payload', diffusion_constant: float = None, potentials: bool = False):
        if diffusion_constant == None:
            if self.diffusion_constant != None:
                diffusion_constant = self.diffusion_constant
            elif self.diffusion_dictionary != None:
                diffusion_constant = self.diffusion_dictionary[name]
            else:
                logger.error(f'No diffusion constant provided for {name}!')
        self.insert_species(name, diffusion_constant, positions)
        if potentials:
            self.manager.add('lj', name, 'all', **self._kwargs)
        return