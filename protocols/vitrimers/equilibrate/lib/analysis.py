#!/usr/bin/env python
"""Takes LAMMPS dump snapshots and outputs density profiles
and the radial potential energy.
"""
from typing import List
from pathlib import Path
import yaml
import re

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import subprocess 

from microgel import Microgel
from enzyme import EnzymeContainer
from writer import EnzymeWriter, MicrogelWriter
from add_enzymes import main as add_enzymes

from softnanotools.logger import Logger
logger = Logger('ANALYSIS')

class Container:
    def __init__(
        self, 
        config: str, 
        lammps: str,
        input_file: str,
        bin_width: str,
        potential: dict,
        output: str,
        enzymes: int,
        seeds: int,
        box: float = None,
        dump: str = 'dump',
        
    ):
        self.config = config
        self.lammps = lammps
        self.input_file = input_file
        self.bin_width = bin_width
        self.potential = potential
        self.output = output
        self.enzymes = enzymes
        self.seeds = seeds
        self.dump = dump
        self.box = box

        logger.info(
            'Initialised Analysis Container with:'
            f'\n\tconfig     : {self.config}'
            f'\n\tlammps     : {self.lammps}'
            f'\n\tinput file : {self.input_file}'
            f'\n\tbin width  : {self.bin_width}'
            f'\n\tpotential  : {self.potential}'
            f'\n\toutput     : {self.output}'
            f'\n\tenzymes    : {self.enzymes}'
            f'\n\tseeds      : {self.seeds}'
            f'\n\tbox        : {self.box}'
            f'\n\tdump       : {self.dump}'
        )

        self.enzyme_writer = EnzymeWriter()
        self.microgel_writer = MicrogelWriter()

        # add enzymes
        logger.info('Calling add_enzymes...')
        add_enzymes(self.enzymes, self.config, self.output, self.box)
        logger.info('Done!')

    def simulate(self):
        """Creates a set of simulations that outputs dumpfiles to be analysed
        """

        # create dump folder
        Path(self.dump).mkdir(exist_ok=True)

        # unwrap lammps command
        lammps = self.lammps.split()

        
        with open(self.input_file, 'r') as f:
            input_file_str = f.read()

        # iterate over each seed
        for seed in range(1, self.seeds + 1):

            # run simulation
            screen = f'simulation.{seed}.screen'

            # create new input_file with 
            #  - different seed
            temp_str = re.sub(
                "(variable seed equal) (.*)", 
                f"\\1 {seed}", 
                input_file_str
            )
            
            #  - different dump path
            temp_str = re.sub(
                f"dump(/dump.*.\*)", 
                f"{self.dump}\\1.{seed}", 
                temp_str
            )

            #  - different config file
            temp_str = re.sub(
                "(variable fname string) (.*)", 
                f"\\1 {self.output}", 
                temp_str
            )

            #  - different output file
            temp_str = re.sub(
                "(variable output string) (.*)", 
                f"\\1 {self.output}.{seed}", 
                temp_str
            )

            # create temp file for simulation
            temp = f'{self.input_file}.{seed}'
            with open(temp, 'w') as f:
                f.write(temp_str)

            # setup command and run
            command = lammps + ['-i', temp, '-sc', screen]
            logger.info(f'Running simulation with command {" ".join(command)}')
            logger.info(f'See {screen} for progress...')
            subprocess.check_output(command)
            logger.info(f'Done')

        return

    def run(self, simulate: bool = True):

        # run simulations
        if simulate:
            self.simulate()

        # create un-averaged table for
        raw = pd.DataFrame()

        enzymes = Path('dump').glob('dump.enzyme.*.*')
        gels = Path('dump').glob('dump.gel.*.*')

        # iterate over all names
        self.enzyme_writer.process_files(enzymes, bin_width=self.bin_width, box=self.box)
        self.microgel_writer.process_files(
            gels, 
            bin_width=self.bin_width, 
            potential_settings=self.potential,
            box=self.box
        )

        return

def main(settings):
    with open(settings, 'r') as f:
        data = yaml.safe_load(f)

    c = Container(**data)
    c.simulate()

    return

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('settings')
    main(parser.parse_args().settings)