#!/usr/bin/env python
"""
pytest script for testing utils folder
"""
import typing
from pathlib import Path
import numpy as np

from hydrogels.utils import *
from hydrogels.utils import simulation
from hydrogels.utils import system
from hydrogels.utils import topology

import pytest

FOLDER = Path(__file__).absolute().parent
OUT = FOLDER / '_out.h5'

def test_topology():
    top = topology.Topology('polymer')
    assert top.is_valid

    top.add_names('Hello')
    top.add_names(['Goodbye'])
    with pytest.raises(SystemError):
        top.add_names(111)

    top.names = ['A', 'B', 'C']

    top = topology.Topology(
        'polymer',
        sequence=['A', 'A', 'A'],
        positions=np.array([
            [0., 0., 0.],
            [0., 0., 1.],
            [0., 0., 2.],
        ]),
        edges=[(0, 1), (1, 2), (2, 0)]
    )
    assert top.connected
    xyz_path = Path(__file__).parent / 'test.xyz'
    top.export_xyz(xyz_path)
    xyz_path.unlink()

def test_system():
    sys = system.System([10., 10., 10.,])
    sys.insert_species('a', 1.0, np.array([[1.0, 0.0, 0.0], [2.0, 0.0, 0.0]]))
    sys.manager.add('lj', 'all', 'all', epsilon=1.0, sigma=1.0, cutoff=2.0)
    print(sys.potential_list)
    simulation = sys.initialise_simulation(fout=str(OUT))
    # create checkpoint
    simulation.make_checkpoints(1, output_directory=str(FOLDER), max_n_saves=1)

    # run
    simulation.run(10, 0.1)

    # load from checkpoint
    simulation = sys.initialise_simulation(checkpoint_directory=FOLDER)

    # run
    simulation.run(10, 0.1)

    # delete output file
    OUT.unlink()
    for target in FOLDER.glob('checkpoint_*'):
        target.unlink()


if __name__=='__main__':
    test_topology()
    test_system()
