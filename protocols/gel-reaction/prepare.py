import yaml

import pandas as pd
import numpy as np
import scipy.spatial.distance as ssd

import subprocess

from softnanotools.runner import Runner
from softnanotools.logger import Logger
logger = Logger(__name__)

from model import read_lammps_conf as read # type: ignore

LMP_HEADERS = [
    'id', 
    'mol', 
    'type', 
    'x', 
    'y', 
    'z', 
    'null_0', 
    'null_1', 
    'null_2'
]

class Model(Runner):
    def __init__(self, settings: dict):
        with open(settings, 'r') as f:
            self.settings = yaml.safe_load(f)
        self.data = read(self.settings['initial'])
        self.radius = self.get_radius()
    
    def get_radius(self) -> float:
        particles = self.data['particles'].copy()
        positions = particles[['x', 'y', 'z']].to_numpy()
        center = positions.mean(0)

        # normalized positions
        normed_positions = positions - center[None,:]

        gyration = np.einsum(
            'im,in->mn', 
            normed_positions,normed_positions
        )
        gyration = gyration/len(positions)
        r = np.sqrt(
                np.sum(
                    [gyration[i][i] for i in range(2)]
                )
            )
        logger.debug(f'Calculating Radius as: {r} from gyration:\n{gyration}')
        return r

    def add_enzyme(self, N: int):
        # add particles
        particles = pd.DataFrame(columns=LMP_HEADERS)
        particles['id'] = np.arange(
            self.data['atoms'] + 1, 
            self.data['atoms'] + N + 1
        )
        particles['mol'] = len(particles) * [2]
        particles['type'] = len(particles) * [self.data['atom_types'] + 1]
        r = self.radius
        box = self.settings['box']
        particles['x'] = \
            np.random.uniform(size=N, low=r, high=box[0]) - box[0]/2
        particles['y'] = \
            np.random.uniform(size=N, low=r, high=box[1]) - box[1]/2
        particles['z'] = \
            np.random.uniform(size=N, low=r, high=box[2]) - box[2]/2
        
        # use self.radius
        # use self.settings['box']
        # add particles in a uniform hollow sphere between these radii

        self.data['particles'] = pd.concat([self.data['particles'], particles])
        self.data['atom_types'] += 1
        self.data['atoms'] += N
        return
    
    def add_payload(self, N: int):
        # add particles
        particles = pd.DataFrame(columns=LMP_HEADERS)
        particles['id'] = np.arange(
            self.data['atoms'] + 1, 
            self.data['atoms'] + N + 1
        )
        particles['mol'] = len(particles) * [3]
        particles['type'] = len(particles) * [self.data['atom_types'] + 1]
        r = self.radius
        particles['x'] = \
            np.random.uniform(size=N, low=0, high=r) - r/2
        particles['y'] = \
            np.random.uniform(size=N, low=0, high=r) - r/2
        particles['z'] = \
            np.random.uniform(size=N, low=0, high=r) - r/2
        

        self.data['particles'] = pd.concat([self.data['particles'], particles])
        self.data['atom_types'] += 1
        self.data['atoms'] += N
        # use self.radius
        # add particles in a uniform sphere inside this radius
        return
    
    @Runner.task(0)
    def add_particles(self):
        self.add_enzyme(self.settings['enzyme'])
        if self.settings['payload']:
            self.add_payload(self.settings['payload'])
        return

    @Runner.task(1)
    def write_lammps_data(self):
        # write to self.settings['final']
        box = self.settings['box']


        with open(self.settings['final'], 'w') as f:
            f.write('New configuration\n\n')
            f.write(f"{self.data['atoms']} atoms\n")
            f.write(f"{self.data['atom_types']} atom types\n")
            f.write(f"{self.data['bonds']} bonds\n")
            f.write(f"{self.data['bond_types']} bond types\n\n")
            f.write(f"{-box[0]/2} {box[0]/2} xlo xhi\n")
            f.write(f"{-box[1]/2} {box[1]/2} ylo yhi\n")
            f.write(f"{-box[2]/2} {box[2]/2} zlo zhi\n\n")
            f.write(f"Masses\n\n")
            for i in range(self.data['atom_types']):
                if i > 2:
                    f.write(f"{i+1} 10\n")
                else:
                    f.write(f"{i+1} 1\n")
            f.write(f"\nAtoms\n\n")
            particles = self.data['particles'].copy()
            particles['null_0'] = len(particles) * [0] 
            particles['null_1'] = len(particles) * [0]
            particles['null_2'] = len(particles) * [0]
            particles.to_csv(
                f, 
                sep=' ', 
                header=False, 
                index=False
            )
            f.write(f"\nBonds\n\n")
            self.data['edges'].to_csv(
                f, 
                sep=' ', 
                header=False, 
                index=False
            )
        return

    @Runner.task(2)
    def run_equilibration(self):
        # run using settings['lammps'] -i settings['input']
        lammps = self.settings['lammps'].split()

        lammps += ['-i', self.settings['input']]
        try:
            logger.info('Running LAMMPS...')
            subprocess.check_output(lammps)
        except KeyboardInterrupt:
            logger.info('LAMMPS stopped by user with Ctrl+C')
        logger.info('Simulation Complete')
        return

def main(settings, run: bool = False):
    model = Model(settings)
    skip = 2
    if run:
        skip = None
    model.execute(skip=skip)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('settings')
    parser.add_argument('-r', '--run', action='store_true')
    main(**vars(parser.parse_args()))