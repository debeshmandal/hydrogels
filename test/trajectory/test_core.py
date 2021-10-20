from pathlib import Path

from hydrogels.trajectory.core import (
    ParticleFrame,
    ParticleTrajectory,
    TopologyFrame,
    TopologyTrajectory
)

import h5py

FOLDER = Path(__file__).parent
H5 = FOLDER / '_test.h5'

def test_ParticleFrame():
    try:
        if h5py.h5.HDF5_VERSION_COMPILED_AGAINST[1] < 10:
            return
    except:
        return

    traj = ParticleTrajectory(H5)
    frame = traj.frames[0]
    frame.array
    frame.dataframe
    output = FOLDER / 'lammps.test.conf'
    frame.to_LAMMPS_dump(output)
    output.unlink()
    return

def test_ParticleTrajectory():
    try:
        if h5py.h5.HDF5_VERSION_COMPILED_AGAINST[1] < 10:
            return
    except:
        return
    traj = ParticleTrajectory(H5)
    traj.time
    traj.frames
    traj.box
    return

def test_TopologyFrame():
    try:
        if h5py.h5.HDF5_VERSION_COMPILED_AGAINST[1] < 10:
            return
    except:
        return
    traj = TopologyTrajectory(H5)
    frame = traj.frames[0]
    frame.dataframe

def test_TopologyTrajectory():
    try:
        if h5py.h5.HDF5_VERSION_COMPILED_AGAINST[1] < 10:
            return
    except:
        return
    traj = TopologyTrajectory(H5)
    traj.time
    traj.frames

def test_LAMMPS_output():
    try:
        if h5py.h5.HDF5_VERSION_COMPILED_AGAINST[1] < 10:
            return
    except:
        return
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

    return

if __name__ == '__main__':
    test_ParticleFrame()
    test_ParticleTrajectory()
    test_TopologyFrame()
    test_TopologyTrajectory()
    test_LAMMPS_output()