from pathlib import Path
import h5py
from softnanotools.logger import Logger
logger = Logger(__name__)

from hydrogels.trajectory.core import ParticleTrajectory, TopologyTrajectory

FOLDER = Path(__file__).parent
H5 = FOLDER / '_test.h5'

def test_write_LAMMPS_dump():
    try:
        traj = ParticleTrajectory(H5)
        frame = traj.frames[0]
        frame.array
        frame.dataframe
        output = FOLDER / 'lammps.test.dump'
        frame.to_LAMMPS_dump(output)
        output.unlink()
    except RuntimeError:
        logger.warning(
            f'HDF5 Version is {h5py.version.hdf5_version} and'
            ' it failed to open a properly tested file'
        )
    return

def test_write_LAMMPS_configuration():
    try:
        traj = ParticleTrajectory(H5)
        particles = traj.frames[0]
        traj = TopologyTrajectory(H5)
        topology = traj.frames[0]

        output = FOLDER / 'lammps.test.conf'
        particles.to_LAMMPS_configuration(output, topology)
        output.unlink()
    except RuntimeError:
        logger.warning(
            f'HDF5 Version is {h5py.version.hdf5_version} and'
            ' it failed to open a properly tested file'
        )
    return

if __name__ == '__main__':
    test_write_LAMMPS_dump()
    test_write_LAMMPS_configuration()