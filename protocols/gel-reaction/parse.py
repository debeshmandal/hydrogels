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

def read_settings(settings: dict) -> hydrogels.System:
    simulation = settings['simulation']
    system = hydrogels.System(simulation['box'])

    reader = get_reader(settings['reader'])
    reader.configure(
        system, 
        **settings
    )

    logger.debug(f'Species:\n{reader.species}')
    logger.debug(f'Topology Species:\n{system.topology_species_list}')

    for potential in settings['potentials']:
        system.add_potential(**potential)

    system.configure_potentials()
    
    return system

