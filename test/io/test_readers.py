from pathlib import Path

import numpy as np

from hydrogels.utils.io import CoreReader, LAMMPSDataReader, AutoReader, HydrogelsReader

PATH = (Path(__file__).parents[0] / '_assets').resolve()

def test_CoreReader():
    reader = CoreReader()
    reader.add_topology(
        'top', 
        ['A', 'A', 'A'], 
        np.array([
            [1.0, 0., 0.],
            [2.0, 0., 0.],
            [3.0, 0., 0.]
        ]), 
        [(0, 1), (0, 2), (1, 2)],
    )
    reader.add_particles(
        'part',
        np.array([
            [0., 0., 0.,],
        ])
    )
    reader.metadata['box'] = np.array([10., 10., 10.])
    system = reader.system(
        diffusion_constant=1.0,
        bonding={
            'top': {
                'kind': 'harmonic',
                'species_1': 'A',
                'species_2': 'A',
                'length': 1.0,
                'force_constant': 1.0,
            }
        }
    )
    simulation = system.initialise_simulation()
    simulation.run(10, 0.1)
    return

def test_HydrogelsReader():
    fname = f"{PATH}/hy.test.gel"
    return

def test_LAMMPSDataReader():
    fname = f"{PATH}/lammps.test.conf"
    reader = LAMMPSDataReader(fname, names=['top'], species={1: 'A', 2: 'A'})
    system = reader.system(
        diffusion_constant=1.0,
        bonding={
            'top': {
                'kind': 'harmonic',
                'species_1': 'A',
                'species_2': 'A',
                'length': 1.0,
                'force_constant': 1.0,
            }
        }
    )
    simulation = system.initialise_simulation()
    simulation.run(10, 0.1)    
    return

def test_AutoReader():
    reader = AutoReader(f"{PATH}/lammps.test.conf")
    reader = AutoReader(f"{PATH}/hy.test.gel")
    return

if __name__ == '__main__':
    test_CoreReader()
    test_LAMMPSDataReader()