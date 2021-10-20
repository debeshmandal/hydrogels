from pathlib import Path
import h5py

from hydrogels.trajectory.core import ParticleTrajectory, TopologyTrajectory

FOLDER = Path(__file__).parent
H5 = FOLDER / '_test.h5'

def test_write_LAMMPS_dump():
    try:
        if h5py.h5.HDF5_VERSION_COMPILED_AGAINST[1] < 10:
            return
    except:
        return
    traj = ParticleTrajectory(H5)
    frame = traj.frames[0]
    frame.array
    frame.dataframe
    output = FOLDER / 'lammps.test.dump'
    frame.to_LAMMPS_dump(output)
    output.unlink()
    return

def test_write_LAMMPS_configuration():
    try:
        if h5py.h5.HDF5_VERSION_COMPILED_AGAINST[1] < 10:
            return
    except:
        return
    traj = ParticleTrajectory(H5)
    particles = traj.frames[0]
    traj = TopologyTrajectory(H5)
    topology = traj.frames[0]

    output = FOLDER / 'lammps.test.conf'
    particles.to_LAMMPS_configuration(output, topology)
    output.unlink()
    return

if __name__ == '__main__':
    test_write_LAMMPS_dump()
    test_write_LAMMPS_configuration()