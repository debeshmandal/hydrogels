import yaml
import json

import numpy as np

from softnanotools.logger import Logger
logger = Logger('simulation')

import hydrogels
from hydrogels.utils.io import AutoReader
from hydrogels.systems import EnzymaticDegradation
from hydrogels import Topology

import tools

def get_reader(settings):
    reader = AutoReader(**settings)
    return reader

def generate_system(settings):
    reader = get_reader(settings['reader'])
    box = settings['box']
    system_settings = {
        'diffusion_dictionary': settings.get('diffusion_dictionary', None),
        'diffusion_constant': settings.get('diffusion_constant', None)
    }
    system = EnzymaticDegradation(
        settings['box'],
        **system_settings, 
    )
    reader.configure(system, **settings)  

    if False:
        system.add_enzyme(np.array([
            [20., 0., 0.],
            [20., 1., 0.],
            [20., 2., 0.],
            [20., 3., 0.],
            [20., 4., 0.],
            [20., 5., 0.],
            [20., 6., 0.],
            [20., 7., 0.],
            [20., 8., 0.],
            [20., 9., 0.],
        ]))
        system.add_payload(np.array([[23., 0., 0.]]))

    logger.debug(
        f'System:\n'
        f'{system.species_list}\n'
    )
    for potential in settings['potentials']:
        logger.debug(f'Adding potential:\n{json.dumps(potential, indent=2)}')
        system.add_potential(**potential)

    system.register_gels()
    logger.info(f'Species: {system.species_list}')
    logger.info(f'Topologies: {system.topology_list}')
    logger.info(f'Topology Species: {system.topology_species_list}')
    for particle in ['monomer', 'unbonded']:
        system.potentials.add_sphere(
            particle_type=particle, 
            force_constant=5.0, 
            origin=[0., 0., 0.], 
            radius=4.0, 
            inclusion=True
        )
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