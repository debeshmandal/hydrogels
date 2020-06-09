#!/usr/bin/env python
"""
Objects for handling commonly used high-level readdy topologies
"""
import typing

import numpy as np
import pandas as pd
import readdy

from readdy._internal.readdybinding.api import TopologyRecord
from readdy._internal.readdybinding.common.util import TrajectoryParticle

class Topology():
    """
    Wrapper for a readdy topology
    """
    def __init__(self, top_type : str, sequence = [], positions = []):
        self.top_type = top_type
        self.sequence = sequence
        self.positions = np.array(positions)

    @property
    def is_valid(self) -> bool:
        return len(self.sequence) == len(self.positions)

    def import_dataframe(self, dataframe : pd.DataFrame):
        """
        Parse a dataframe containing information on 
        the sequences and positions of a topology
        and pass this information to the Topology object
        """
        self.sequence = dataframe['sequence']
        self.positions = dataframe.iloc[:, 1:4].values

    @property
    def dataframe(self) -> pd.DataFrame:
        """
        DataFrame form of sequence and positions
        """
        data = {
            'sequence' : self.sequence,
            'x' : self.positions[:, 0],
            'y' : self.positions[:, 1],
            'z' : self.positions[:, 2]
        }
        output = pd.DataFrame(data)

    def export_xyz(self, fout : str):
        """
        Export to xyz file, readable by OVITO
        """
        self.dataframe.to_csv(fout, index=False, header=False, float_format="%g", sep='\t')

    def add_to_sim(self, simulation : readdy.Simulation):
        """
        Adds the topology to a readdy simulation
        """
        simulation.add_topology(
            self.top_type,
            self.sequence,
            self.positions
        )

class ReaddyTopology(Topology):
    """
    Class to handle readdy.Topology objects
    """
    def __init__(
        self, 
        topology : TopologyRecord, 
        particles : typing.List[TrajectoryParticle]):
        pass
