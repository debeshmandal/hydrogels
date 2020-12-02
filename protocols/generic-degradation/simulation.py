import yaml
import json

from softnanotools.logger import Logger
logger = Logger('simulation')

import hydrogels
from hydrogels.utils.io import AutoReader
from hydrogels.systems import EnzymaticDegradation

import tools

def get_reader(settings):
    reader = AutoReader(**settings)
    return reader

def generate_system(settings):
    reader = get_reader(settings['reader'])
    system = EnzymaticDegradation(
        settings['box'],
        **settings['simulation'], 
    )
    logger.debug(
        f'System:\n'
        f'{system.species_list}\n'
    )
    reader.configure(system, **settings)
    system.register_gels()
    logger.info(f'Species: {system.species_list}')
    for potential in settings['potentials']:
        logger.debug(f'Adding potential:\n{json.dumps(potential, indent=2)}')
        system.add_potential(**potential)
    return system

def run_simulation(system, settings):
    sim = system.initialise_simulation()

    _settings = settings['simulation']
    length = _settings['length']
    stride = _settings['stride']
    timestep = _settings['timestep']

    sim.observe.topologies(stride)
    sim.observe.particles(stride)
    sim.record_trajectory(stride)
    sim.run(length * stride, timestep)
    return sim

def main(fname: str):
    settings = tools.parse_yaml(fname)
    system = generate_system(settings)
    sim = run_simulation(system, settings)
    return

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('fname')
    main(**vars(parser.parse_args()))