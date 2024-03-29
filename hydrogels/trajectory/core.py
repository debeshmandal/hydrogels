#!/usr/bin/env python
"""core.py - auto-generated by softnanotools"""
from pathlib import Path
from typing import Iterable, Union, List, Tuple

import numpy as np
import pandas as pd
from pandas.core import frame

from softnanotools.logger import Logger
logger = Logger(__name__)

import readdy
from readdy._internal.readdybinding.common.util import ( # type: ignore
    TrajectoryParticle,
)

from readdy._internal.readdybinding.api import ( # type: ignore
    TopologyRecord
)

from .lammps import write_LAMMPS_dump, write_LAMMPS_configuration

class ParticleFrame():
    def __init__(self, frame: List[TrajectoryParticle], box: np.ndarray):
        self.time = frame[0].t
        self.box = box
        data = {
            'x': [],
            'y': [],
            'z': [],
            'id': [],
            'type': [],
            'flavor': [],
            'mol': [],
        }
        for particle in frame:
            data['x'].append(particle.position[0])
            data['y'].append(particle.position[1])
            data['z'].append(particle.position[2])
            data['id'].append(particle.id)
            data['type'].append(particle.type)
            data['flavor'].append(particle.flavor)
            data['mol'].append(1)

        self.dataframe = \
            pd.DataFrame(data).sort_values('id').reset_index(drop=True)

        del data

    @property
    def array(self) -> np.ndarray:
        return self.dataframe[['x', 'y', 'z']].to_numpy()

    def assign_molecule(self, topology: "TopologyFrame"):
        self.dataframe['mol'] = \
            self.dataframe['id'].apply(lambda x: topology.molecules.get(x, -1))
        p = max(self.dataframe['mol']) + 1
        self.dataframe['mol'] = self.dataframe['mol'].apply(
            lambda x: p if x == -1 else x
        )
        return

    def count_atoms(self) -> dict:
        """Returns a dictionary containing the number of each atom type
        """
        types = self.dataframe['type']
        return {i: len(types[types == i]) for i in set(types)}

    def to_LAMMPS_dump(self, fname: Union[str, Path]):
        write_LAMMPS_dump(
            self.dataframe,
            fname,
            self.time,
            self.box,
        )

    def to_LAMMPS_configuration(
        self,
        fname: Union[str, Path],
        topology: "TopologyFrame",
        masses: Iterable = None,
        comment: str = None,
    ):
        self.assign_molecule(topology)
        write_LAMMPS_configuration(
            self.dataframe,
            topology.dataframe,
            fname,
            self.box,
            masses=masses,
            comment=comment,
        )

    def translate(self, new: Iterable):
        """Translates entire frame TO new centre of mass

        Arguments:
            new: New position for centre of mass
        """
        x = new[0]
        y = new[1]
        z = new[2]
        averages = self.dataframe.mean()
        self.dataframe['x'] += x - averages['x']
        self.dataframe['y'] += y - averages['y']
        self.dataframe['z'] += z - averages['z']
        return

class ParticleTrajectory():
    """Class for storing positions of particles outputted from
    a simulation using ReaDDy"""
    def __init__(self, fname: Union[str, Path]):
        logger.info(f'Reading ReaDDy trajectory from {fname}')
        fname = Path(fname)
        _traj = readdy.Trajectory(str(fname.absolute()))
        _raw = _traj.read()

        self.box = _traj.box_size
        self.particle_types = _traj.particle_types
        self._time, self._frames = self.load(_raw, self.box)

        del _traj
        del _raw

    @staticmethod
    def load(
        trajectory: list,
        box: np.ndarray
    ) -> Tuple[np.ndarray, List[ParticleFrame]]:

        _frames = [ParticleFrame(f, box) for f in trajectory]
        _time = np.array([f.time for f in _frames])

        return _time, _frames

    @property
    def time(self) -> np.ndarray:
        return self._time

    @property
    def frames(self) -> List[ParticleFrame]:
        return self._frames

    def count_atoms(self) -> pd.DataFrame:
        """Returns a dataframe containing the number of
        each atom type at each timestep
        """
        result = pd.DataFrame()
        result['t'] = self.time

        particles = [frame.count_atoms() for frame in self.frames]
        for particle_type in self.particle_types:
            result[particle_type] = [i.get(particle_type, 0) for i in particles]

        return result

    def to_LAMMPS_dump(self, fname: Union[str, Path]):
        """Writes the whole trajectory to LAMMPS dump
        format files"""
        for frame in self.frames:
            write_LAMMPS_dump(
                frame.dataframe,
                str(Path(fname).absolute()) + f'.{frame.time}',
                frame.time,
                frame.box,
                types=list(
                    sorted(
                        self.particle_types,
                        key=lambda x: self.particle_types[x]
                    )
                )
            )

    def to_LAMMPS_configuration(
        self,
        fname: Union[str, Path],
        topology: "TopologyTrajectory",
        masses: Iterable = None,
        comment: str = None,
    ):
        """Writes the whole trajectory to LAMMPS configuration
        format files"""
        frames = self.frames
        for i, topology_frame in enumerate(topology.frames):
            frame = frames[i]
            frame.assign_molecule(topology_frame)
            write_LAMMPS_configuration(
                frame.dataframe,
                topology_frame.dataframe,
                str(Path(fname).absolute()) + f'.{frame.time}',
                self.box,
                masses=masses,
                comment=comment,
                types=list(
                    sorted(
                        self.particle_types,
                        key=lambda x: self.particle_types[x]
                    )
                )
            )

class TopologyFrame():
    def __init__(self, frame: List[TopologyRecord]):
        data = {
            'id': [],
            'type': [],
            'atom_1': [],
            'atom_2': []
        }
        self.molecules = {}
        count = 1
        for i, molecule in enumerate(frame):
            particles = molecule.particles
            edges = molecule.edges

            bonds = [
                (particles[edge[0]], particles[edge[1]]) for
                edge in edges
            ]
            molecule_number = i + 1
            for particle in particles:
                self.molecules[particle] = molecule_number

            for bond in bonds:
                data['id'].append(count)
                data['type'].append(1)
                data['atom_1'].append(bond[0])
                data['atom_2'].append(bond[1])
                count += 1

        self.dataframe = pd.DataFrame(data)

        del data

    def count_bonds(self) -> dict:
        """Returns the number of bonds in the frame
        """
        return len(self.dataframe)

    def to_LAMMPS_configuration(
        self,
        fname: Union[str, Path],
        particles: "ParticleFrame",
        masses: Iterable = None,
        comment: str = None,
    ):
        particles.assign_molecule(self)
        write_LAMMPS_configuration(
            particles.dataframe,
            self.dataframe,
            fname,
            particles.box,
            masses=masses,
            comment=comment,
        )

class TopologyTrajectory():
    def __init__(self, fname: Union[str, Path]):
        logger.info(f'Reading ReaDDy trajectory from {fname}')
        fname = Path(fname)
        _traj = readdy.Trajectory(str(fname.absolute()))
        _raw = _traj.read_observable_topologies()

        self._time, self._frames = self.load(_raw)

        del _traj
        del _raw

    @staticmethod
    def load(trajectory: tuple) -> Tuple[np.ndarray, List[TopologyFrame]]:
        _time = np.array(trajectory[0])
        _frames = [TopologyFrame(f) for f in trajectory[1]]
        return _time, _frames

    @property
    def time(self) -> np.ndarray:
        return self._time

    @property
    def frames(self) -> List[TopologyFrame]:
        return self._frames

    def count_bonds(self) -> pd.DataFrame:
        """Returns a dataframe containing the number of
        each bonds at each timestep
        """
        return pd.DataFrame({
            't': self.time,
            'bonds': [frame.count_bonds() for frame in self.frames]
        })

    def to_LAMMPS_configuration(
        self,
        fname: Union[str, Path],
        particles: ParticleTrajectory,
        masses: Iterable = None,
        comment: str = None,
    ):
        frames = self.frames
        for i, particles_frame in enumerate(particles.frames):
            frame = frames[i]
            particles_frame.assign_molecule(frame)
            write_LAMMPS_configuration(
                particles_frame.dataframe,
                frame.dataframe,
                str(Path(fname).absolute()) + f'.{particles_frame.time}',
                particles_frame.box,
                masses=masses,
                comment=comment,
                types=list(
                    sorted(
                        particles.particle_types,
                        key=lambda x: particles.particle_types[x]
                    )
                )
            )

if __name__ == '__main__':
    import doctest
    doctest.testmod()
