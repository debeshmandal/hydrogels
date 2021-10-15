from pathlib import Path

from hydrogels.trajectory.core import ParticleTrajectory

FOLDER = Path(__file__).parent
H5 = FOLDER / '_test.h5'

def test_write_LAMMPS_dump():
    traj = ParticleTrajectory(H5)
    frame = traj.frames[0]
    frame.array
    frame.dataframe
    output = FOLDER / 'lammps.test.conf'
    frame.to_LAMMPS_dump(output)
    output.unlink()
    return

if __name__ == '__main__':
    test_write_LAMMPS_dump()