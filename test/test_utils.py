#!/usr/bin/env python
"""
pytest script for testing utils folder
"""
import typing

import numpy as np

from hydrogels.utils import *
from hydrogels.utils import simulation
from hydrogels.utils import system
from hydrogels.utils import topology

def test_topology():
    top = topology.Topology('polymer')
    assert top.is_valid

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


