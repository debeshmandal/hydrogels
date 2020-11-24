import numpy as np
import pandas as pd

from .core import Gel

from ...utils.io import AutoReader

class GenericGel(Gel):
    """Topology of a gel network that can be read from a CSV file"""
    def __init__(self, fname: str, top_type: str, reader=AutoReader, **kwargs):
        _reader = reader(fname)
        super().__init__(
            top_type, 
            positions=_reader.positions, 
            edges=_reader.edges, 
            **kwargs
        ) 
