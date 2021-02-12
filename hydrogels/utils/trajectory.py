import pandas as pd

import readdy

class TrajectoryFrame():
    def __init__(self, trajectory: "Trajectory", frame: int):
        pass

    @staticmethod
    def extract_frame(trajectory: "Trajectory", frame: int):
        return

    @property
    def particles(self) -> pd.DataFrame:
        return

    @property
    def molecules(self) -> list:
        """Returns a list of containerised particles
        
        If particles belong to a topology, this is noted as a molecule. 
        Otherwise particles with a normal flavor will be part of a single 
        molecule.
        """
        return

    def write_lammps_conf(self, fname: str):
        return

class Trajectory(readdy.Trajectory):
    def __init__(*args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_frame(self, frame: int):
        return TrajectoryFrame(self, frame)
    