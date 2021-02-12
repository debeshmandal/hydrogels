import yaml

from softnanotools.logger import Logger
logger = Logger(__name__)

from parse import read_settings # type: ignore

def main(**kwargs):
    logger.info('Running...')
    system = read_settings(kwargs)
    sim = system.initialise_simulation()
    _settings = settings['simulation']
    #sim.observe.forces(stride=_settings['stride'])
    #sim.observe.energy(stride=_settings['stride'])
    length = _settings['length']
    stride = _settings['stride']
    timestep = _settings['timestep']

    sim.observe.topologies(stride)
    sim.observe.particles(stride)
    sim.record_trajectory(stride)
    sim.run(length * stride, timestep)
    return

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('settings')
    with open(parser.parse_args().settings, 'r') as f:
        settings = yaml.safe_load(f)
    main(**settings)