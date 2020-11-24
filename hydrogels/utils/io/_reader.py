from ._core import CoreReader
from ._lammps import LAMMPSDataReader

class AutoReader(CoreReader):
    readers = {
        'lammps_data': LAMMPSDataReader,
    }
    
    def __init__(self, fname):
        self.fname = fname

    def detect_filetype(self):
        return