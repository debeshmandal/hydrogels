#!/usr/bin/env python
"""
pytest script for testing utils folder
"""
import typing

from hydrogels.utils import *
from hydrogels.utils import simulation
from hydrogels.utils import system
from hydrogels.utils import topology

def test_topology() -> bool:
    top = topology.Topology('polymer')
    assert top.is_valid
