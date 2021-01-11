from pathlib import Path

import subprocess
import re

import pandas as pd
import numpy as np

from softnanotools.logger import Logger
logger = Logger('SIMULATION')

def read_lammps_conf(fname):
    data = {}
    with open(fname, 'r') as f:

        # skip first two lines
        f.readline()
        f.readline()

        # read atom + bond types
        logger.debug(f'Setting...')
        for i in range(4):
            line = f.readline().split()
            value = line[0]
            label = '_'.join(line[1:])
            logger.debug(f'    {label}{" " * (10 - len(label))}\t-> {value}')
            data[label] = int(value)

        for i, line in enumerate(f.readlines()):
            if re.findall('Atoms', line):
                atoms_line = i+6
                logger.debug(f'Line that atoms start on: {atoms_line}')

            elif re.findall('Bonds', line):
                bonds_line = i+6
                logger.debug(f'Line that bonds start on: {bonds_line}')

    data['particles'] = pd.read_csv(
        fname, 
        skiprows=atoms_line+2,
        header=None,
        delim_whitespace=True,
        nrows=data['atoms']
    ).rename(columns={
        0: 'id',
        1: 'mol',
        2: 'type',
        3: 'x',
        4: 'y',
        5: 'z',
    })[['id', 'mol', 'type', 'x', 'y', 'z']].sort_values(
        by='id'
    ).reset_index(
        drop=True
    )

    logger.debug(f'Particles:\n{data["particles"]}')
    
    data['edges'] = pd.read_csv(
        fname, 
        skiprows=bonds_line+1,
        header=None,
        delim_whitespace=True,
        nrows=data['bonds']
    ).rename(columns={
        0: 'id',
        1: 'type',
        2: 'atom_1',
        3: 'atom_2'
    }).sort_values(by='id').reset_index(drop=True)

    logger.debug(f'Edges:\n{data["edges"]}')

    return data

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('fname')
    parser.add_argument('-T', '--temperature', default=0.05, type=float)
    parser.add_argument('-l', '--lammps', default='lmp_mpi')
    parser.add_argument('-p', '--prefix', default='mpirun -np 4')
    parser.add_argument('-i', '--input-file', default='lammps.main.in')
    args = parser.parse_args()

    # cutoff

    particles = read_lammps_conf(args.fname)['particles']
    delta = [particles[i].max() - particles[i].min() for i in ['x', 'y', 'z']]
    cutoff = int(2 * max(delta))

    # set variables

    with open(args.input_file, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if re.findall('variable fname string', line):
            logger.debug(f'Setting fname in line {i} to {args.fname}')
            lines[i] = f'variable fname string {args.fname}\n'
        if re.findall('variable T equal', line):
            logger.debug(f'Setting T in line {i} to {args.temperature}')
            lines[i] = f'variable T equal {args.temperature}\n'
        if re.findall('variable global_cutoff equal', line):
            logger.debug(f'Setting global_cutoff in line {i} to {cutoff}')
            lines[i] = f'variable global_cutoff equal {cutoff}\n'


    with open(args.input_file, 'w') as f:
        f.write(''.join(lines))

    # run simulation

    if args.prefix:
        subprocess.check_output([
            *args.prefix.split(),
            args.lammps,
            '-i',
            args.input_file
        ])

    else:
        subprocess.check_output(
            args.lammps,
            '-i',
            args.input_file
        )

