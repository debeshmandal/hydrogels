import json

from typing import List, Tuple

import pandas as pd

from softnanotools.logger import Logger
logger = Logger(__name__)

from ..system import System
from ..topology import Topology

from ...generators import Gel

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
        cls = None,
    ):
        if cls == None:
            cls = Topology

        else:
            cls = {
                'Topology': Topology,
                'Gel': Gel,
            }[cls]

        topology = cls(
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
            system = System(self.metadata['box'], unit_system=None)
        else:
            system = System(kwargs['box'], unit_system=None)
        self.configure(system, **kwargs)
        return system

    def configure(
        self,
        system,
        diffusion_constant: float = None,
        diffusion_dictionary: float = None,
        bonding: List[dict] = None,
        **kwargs
    ):
        if diffusion_dictionary != None and diffusion_constant != None:
            raise ValueError('Please provide only one form for the diffusion constants!')

        metadata = self.metadata
        topologies = self._topologies
        particles = self._particles

        logger.debug('Configuring system using reader...')
        logger.debug(f'\tmetadata: {metadata}')
        logger.debug(f'\ttopologies: {topologies}')
        logger.debug(f'\tparticles: {particles}')

        logger.debug('Using reader to insert topologies...')

        for topology in self.topologies:
            logger.info(f'Processing topology: {topology}')
            if topology.top_type not in bonding:
                raise TypeError(
                    f'Topology ({topology.top_type}) has been found'
                    f' but no bonds can be found in the bonding dictionary:'
                    f'\n{json.dumps(bonding, indent=2)}'
                )
            settings = bonding[topology.top_type]
            if isinstance(settings, list):
                topology.add_bond(settings)
            else:
                topology.add_bond(**settings)
            system.insert_topology(
                topology,
                diffusion_dictionary=diffusion_dictionary,
                diffusion_constant=diffusion_constant
            )

        logger.debug(f'Using reader to insert species...')

        if diffusion_constant:
            logger.debug(f'Using diffusion_constant ({diffusion_constant})')
            diffusion = diffusion_constant
            for name, value in self.particles.items():
                logger.debug(f'Adding {name}')
                system.insert_species(name, diffusion, value)

        elif diffusion_dictionary:
            logger.debug(f'Using diffusion_dictionary: {diffusion_dictionary}')
            diffusion = diffusion_dictionary
            for name, value in self.particles.items():
                logger.debug(f'Adding {name}')
                system.insert_species(name, diffusion[name], value)

        return