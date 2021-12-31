from pathlib import Path
from typing import Union
import yaml

from softnanotools.logger import Logger
logger = Logger(__name__)

from parse import read_settings # type: ignore

def main(checkpoint: Path = None, **kwargs):
    logger.info('Running...')
    system = read_settings(kwargs)
    sim = system.initialise_simulation(checkpoint=checkpoint)
    _settings = settings['simulation']
    #sim.observe.forces(stride=_settings['stride'])
    #sim.observe.energy(stride=_settings['stride'])
    length = _settings['length']
    stride = _settings['stride']
    timestep = _settings['timestep']

    sim.observe.topologies(stride)
    sim.observe.particles(stride)
    sim.record_trajectory(stride)
    sim.progress_output_stride = stride
    checkpoints_settings = _settings.get('checkpoints')
    if checkpoints_settings:
        sim.make_checkpoints(**checkpoints_settings)
    sim.run(length * stride, timestep)
    return

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('settings')
    parser.add_argument('--checkpoint', default=None, type=Path)
    args = parser.parse_args()
    with open(args.settings, 'r') as f:
        settings = yaml.safe_load(f)

    main(args.checkpoint, **settings)
