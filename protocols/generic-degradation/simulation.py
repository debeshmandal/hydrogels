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
        **settings['simulation'], 
        topologies=reader.topologies,
    )
    reader.configure(system, **settings)
    return

def generate_simulation(system, stride):
    simu = system.initialise_simulation()
    simu.observe.topologies(stride)
    simu.observe.particles(stride)
    simu.record_trajectory(stride)
    return simu

def main(fname: str):
    settings = tools.parse_yaml(fname)
    system = generate_system(settings)
    simulation = generate_simulation(system)
    simu.run(length * stride, timestep)
    return

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('fname')
    main(**vars(parser.parse_args()))