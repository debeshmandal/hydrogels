import json

from softnanotools.logger import Logger
logger = Logger(__name__)

import hydrogels
from hydrogels.utils.io import AutoReader
from hydrogels.utils.system import PotentialManager
from hydrogels.generators.gels import Gel

def get_reader(settings: dict):
    logger.info('Initialising reader...')
    logger.debug(json.dumps(settings, indent=2))
    reader = AutoReader(**settings)
    return reader

def get_potential_manager(settings: dict):
    logger.info('Initialising potential manager...')
    logger.debug(json.dumps(settings, indent=2))
    return

def get_bonding_manager(settings: dict):
    logger.info('Initialising system...')
    logger.debug(json.dumps(settings, indent=2))
    return

def get_system(settings: dict, reader: AutoReader = None):
    logger.info('Initialising system...')
    logger.debug(json.dumps(settings, indent=2))
    return

def register_reactions(
    system: hydrogels.System, 
    released: str ='released',
    enzyme: str = 'enzyme',
    decay_rate: float = 0.01,
    degradation_rate: float = 0.01,
    radius: float = 1.0,
):
    
    for top in system.topology_list:
        if isinstance(top, Gel):
            # register spatial reaction: enzyme + bonded -> enzyme + unbonded
            top.register_degradation(
                system, 
                enzyme=enzyme,
                rate=degradation_rate,
                radius=radius,
            )
    
            # register structural reaction: unbonded -> released
            top.register_decay(
                system, 
                released=released, 
                rate=decay_rate
            )


def read_settings(settings: dict) -> hydrogels.System:
    simulation = settings['simulation']
    system = hydrogels.System(simulation['box'], unit_system=None)
    system.kbt = 0.05
    logger.info(f'Energy Unit: {system.energy_unit}')
    logger.info(f'Length Unit: {system.length_unit}')
    logger.info(f'Temperature Unit: {system.temperature_unit}')
    reader = get_reader(settings['reader'])
    reader.configure(
        system, 
        **settings
    )

    logger.debug(f'Species:\n{reader.species}')
    logger.debug(f'Topology Species:\n{system.topology_species_list}')

    for potential in settings['potentials']:
        system.add_potential(**potential)
    
    if settings.get('reaction', False):
        logger.debug('Registering reaction with the following settings:')
        logger.debug(json.dumps(settings['reaction'], indent=2))
        register_reactions(system, **settings['reaction'])

    return system

