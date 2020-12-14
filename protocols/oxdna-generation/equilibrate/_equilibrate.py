import subprocess

from pathlib import Path

from softnanotools.logger import Logger
logger = Logger('EQUILIBRATE')

def main(fname: str, lammps: str):
    input_file = Path(__file__).resolve().replace('_equilibrate.py', 'lammps.main.in')
    subprocess.check_output([
        lammps,
        input_file
    ])
    return

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('fname')
    parser.add_argument('-l', '--lammps', default='lmp_mpi')
    main(**vars(parser.parse_args()))
    