#!/usr/bin/env python
"""
pytest script for testing utils folder
"""
import typing

from ..utils import *
from ..utils import simulation
from ..utils import system
from ..utils import topology

def test_topology() -> bool:
    top = topology.Topology('polymer')
    assert top.is_valid
    return True
