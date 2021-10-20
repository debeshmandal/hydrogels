from pathlib import Path

from hydrogels.trajectory.core import (
    ParticleFrame,
    ParticleTrajectory,
    TopologyFrame,
    TopologyTrajectory
)

import h5py

from softnanotools.logger import Logger
logger = Logger(__name__)

FOLDER = Path(__file__).parent
H5 = FOLDER / '_test.h5'

def test_ParticleFrame():
    try:
        traj = ParticleTrajectory(H5)
        frame = traj.frames[0]
        frame.array
        frame.dataframe
        output = FOLDER / 'lammps.test.conf'
        frame.to_LAMMPS_dump(output)
        output.unlink()
    except RuntimeError:
        logger.warning(
            f'HDF5 Version is {h5py.version.hdf5_version} and'
            ' it failed to open a properly tested file'
        )
    return

def test_ParticleTrajectory():
    try:
        traj = ParticleTrajectory(H5)
        traj.time
        traj.frames
        traj.box
    except RuntimeError:
        logger.warning(
            f'HDF5 Version is {h5py.version.hdf5_version} and'
            ' it failed to open a properly tested file'
        )
    return

def test_TopologyFrame():
    try:
        traj = TopologyTrajectory(H5)
        frame = traj.frames[0]
        frame.dataframe
    except RuntimeError:
        logger.warning(
            f'HDF5 Version is {h5py.version.hdf5_version} and'
            ' it failed to open a properly tested file'
        )

def test_TopologyTrajectory():
    try:
        traj = TopologyTrajectory(H5)
        traj.time
        traj.frames
    except RuntimeError:
        logger.warning(
            f'HDF5 Version is {h5py.version.hdf5_version} and'
            ' it failed to open a properly tested file'
        )

def test_LAMMPS_output():

    try:
        topology = TopologyTrajectory(H5)
        particles = ParticleTrajectory(H5)

        dump = FOLDER / 'dump'
        particles.to_LAMMPS_dump(dump)
        for target in FOLDER.glob('dump.*'):
            target.unlink()

        conf = FOLDER / 'conf'
        particles.to_LAMMPS_configuration(conf, topology)
        for target in FOLDER.glob('conf.*'):
            target.unlink()

        topology.to_LAMMPS_configuration(conf, particles)
        for target in FOLDER.glob('conf.*'):
            target.unlink()

    except RuntimeError:
        logger.warning(
            f'HDF5 Version is {h5py.version.hdf5_version} and'
            ' it failed to open a properly tested file'
        )
    return

if __name__ == '__main__':
    test_ParticleFrame()
    test_ParticleTrajectory()
    test_TopologyFrame()
    test_TopologyTrajectory()
    test_LAMMPS_output()