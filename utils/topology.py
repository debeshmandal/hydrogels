#!/usr/bin/env python
"""
Objects for handling commonly used high-level readdy topologies
"""
import readdy
import numpy as np
import pandas as pd
import typing

class Topology():
    """
    Wrapper for a readdy topology
    """
    def __init__(self, top_type : str):
        self.top_type = top_type
        self.sequence = []
        self.positions = np.array([[]])

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
        pass

    def export_xyz(self, fout : str):
        pass

    def add_to_sim(self, simulation : readdy.Simulation):
        """
        Adds the topology to a readdy simulation
        """
        simulation.add_topology(
            self.top_type,
            self.sequence,
            self.positions
        )