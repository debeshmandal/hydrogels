from model import Model as _Model

class Model(_Model):
    def __init__(self, fname: str, box: float):
        self.box = box
        super().__init__(fname)

    def add_enzyme(self, N):
        # add particles
        return
    
    def add_payload(self, N):
        # add particles
        return
    
    def write_lammps_data(self, fname):
        return

    def run_equilibration(self, settings):
        # run without reactions
        return

def main():
    return

if __name__ == '__main__':
    main()