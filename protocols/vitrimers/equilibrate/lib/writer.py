#!/usr/bin/env python
"""Creates an averaging object that takes Microgel
or EnzymeContainer objects and updates a set of raw data
that outputs mean and std over a distributed set of simulations
"""

from pathlib import Path
from os import PathLike
import numpy as np
import pandas as pd

from microgel import Microgel
from enzyme import EnzymeContainer

import json

from typing import Iterable, Union, List

class Writer:
    def __init__(
        self, 
        _type: type, 
        dataframe_keys: List[str] = None,
        value_keys: List[str] = None
    ):
        self._type = _type
        self._objects = []

        self._dataframes = {}
        self._values = {}

        if isinstance(dataframe_keys, Iterable):
            self._dataframes = {key: [] for key in dataframe_keys}

        if isinstance(value_keys, Iterable):
            self._values = {key: [] for key in value_keys}

    def add_object(self, obj: Union[Microgel, EnzymeContainer]):
        assert type(obj) == self._type
        self._objects.append(obj)
    
        return

    def gather_values(self) -> dict:
        values = {}

        for key, value in self._values.items():
            values[key] = {}
            values[key]['mean'] = np.mean(value)
            values[key]['std'] = np.std(value)
            values[key]['raw'] = value

        return values

    def gather_dfs(self) -> dict:

        # create final dictionary
        results = {}

        # iterate over if kind of df
        for kind, df_list in self._dataframes.items():
            results[kind] = pd.DataFrame()

            columns = df_list[0].columns
            for column in columns:
                temp = []
                for df in df_list:
                    temp.append(df[column])

                temp = pd.concat(temp, axis=1)

                results[kind][f'{column}_mean'] = temp.mean(axis=1)
                results[kind][f'{column}_std'] = temp.std(axis=1)

        return results

    def process_files(self, targets: List[PathLike], **kwargs):
        """Take multiple filepaths and collate into the Writer"""
        for target in targets:
            self.add_object(
                self._type(target, **kwargs)
            )
        return

    @property
    def stats(self) -> dict:
        """Returns the mean and std of everything in self._dataframes
        and self._values"""

        
        values = self.gather_values()
        dfs = self.gather_dfs()
        
        return {'values': values, 'dataframes': dfs}

    @property
    def summary(self) -> dict:
        return self.stats

    @property
    def json(self) -> str:
        string = json.dumps(
            self.summary,
            indent=2,
            default=lambda df: df.to_dict('list')
        )
        return string


class MicrogelWriter(Writer):
    def __init__(self):
        super().__init__(
            Microgel,
            dataframe_keys=[
                'density',
                'energy'
            ],
            value_keys=[
                'radius',
                'volume',
                'density',
                'area'
            ],
        )

    def add_object(self, obj: Microgel):
        # do the standard stuff
        super().add_object(obj)

        # do new stuff

        # update dfs
        self._dataframes['density'].append(obj.density_map)
        self._dataframes['energy'].append(obj.energy_map)

        # update values
        self._values['radius'].append(obj.radius)
        self._values['volume'].append(obj.volume)
        self._values['area'].append(obj.area)
        self._values['density'].append(obj.density)

        return

    @property
    def summary(self) -> dict:
        _stats = self.stats
        results = {
            'radius_mean': _stats['values']['radius']['mean'],
            'radius_std': _stats['values']['radius']['std'],
            'volume_mean': _stats['values']['volume']['mean'],
            'volume_std': _stats['values']['volume']['std'],
            'area_mean': _stats['values']['area']['mean'],
            'area_std': _stats['values']['area']['std'],
            'density_mean': _stats['values']['density']['mean'],
            'density_std': _stats['values']['density']['std'],
            'density': pd.DataFrame({
                'r': _stats['dataframes']['density']['r_mean'],
                'mean': _stats['dataframes']['density']['rho_mean'],
                'std': _stats['dataframes']['density']['rho_std'],
            }),
            'energy': pd.DataFrame({
                'r': _stats['dataframes']['energy']['r_mean'],
                'mean': _stats['dataframes']['energy']['mean_mean'],
                'std': _stats['dataframes']['energy']['mean_std'],
            })
        }
        return results


class EnzymeWriter(Writer):
    def __init__(self):
        super().__init__(
            EnzymeContainer,
            dataframe_keys=['density']
        )

    def add_object(self, obj: EnzymeContainer):

        # do the standard stuff
        super().add_object(obj)

        # do new stuff
        self._dataframes['density'].append(obj.density_map)

        return

    @property
    def summary(self) -> dict:
        _stats = self.stats
        results = {
            'density': pd.DataFrame({
                'r': _stats['dataframes']['density']['r_mean'],
                'mean': _stats['dataframes']['density']['rho_mean'],
                'std': _stats['dataframes']['density']['rho_std'],
            }),
        }
        return results

if __name__ == '__main__':

    # Create MicrogelWriter
    microgel_writer = MicrogelWriter()

    # Create EnzymeWriter
    enzyme_writer = EnzymeWriter()

    # Create a Microgel instance and add to writer
    microgel_writer.add_object(
        Microgel('dump/dump.gel.100000.1')
    )

    # Create a EnzymeContainer instance and add to writer
    enzyme_writer.add_object(
        EnzymeContainer('dump/dump.enzyme.100000.1')
    )

    # Repeat but in bulk
    microgel_writer.process_files(
        Path('dump').glob('dump.gel.*.2')
    )

    enzyme_writer.process_files(
        Path('dump').glob('dump.enzyme.*.2')
    )

    # print summary
    print(microgel_writer.json)
    print(enzyme_writer.json)

    

