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
    xyz_path.unlink(missing_ok=True)

def test_system():
    sys = system.System([10., 10., 10.,])
    sys.insert_species('a', 1.0, np.array([[1.0, 0.0, 0.0], [2.0, 0.0, 0.0]]))
    sys.manager.add('lj', 'all', 'all', epsilon=1.0, sigma=1.0, cutoff=2.0)
    print(sys.potential_list)
    simulation = sys.initialise_simulation()
    simulation.run(10, 0.1)

if __name__=='__main__':
    test_topology()
    test_system()


