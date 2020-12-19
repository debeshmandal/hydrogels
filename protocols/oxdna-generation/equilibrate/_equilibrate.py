import subprocess

from pathlib import Path

from softnanotools.logger import Logger
logger = Logger('EQUILIBRATE')

def main(lammps: str, fname: str, input_file: str):
    logger.debug(f'Setting the LAMMPS output data file to {fname}')
    with open(input_file, 'r') as f:
        data = f.readlines()

    data[2] = f"variable fname string {fname}\n"

    with open(input_file, 'w') as f:
        f.write(''.join(data))
    
    logger.info('Running LAMMPS to equilibrate gel...')
    subprocess.check_output([
        lammps,
        '-i',
        input_file,
    ])

    logger.info('Finished running equilibration!')
    return

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('fname')
    parser.add_argument('-l', '--lammps', default='lmp_mpi')
    main(**vars(parser.parse_args()))
    