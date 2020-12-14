from ._lammps import LAMMPSDataReader

class _AutoReader:
    _readers = {
        'lammps-data': LAMMPSDataReader,
    }
    
    def __init__(self, fname, kind='auto', **kwargs):
        if kind == 'auto':
            kind = self.detect_filetype(fname)
        
        self.reader = self._readers[kind](fname, **kwargs)

    def detect_filetype(self, fname):
        raise NotImplementedError(
            'Auto-detection of filetypes has not ' 
            'been implemented yet'
        )

def AutoReader(fname, kind='auto', **kwargs):
    return _AutoReader(fname, kind, **kwargs).reader