import numpy as np
import pandas as pd
import json
import yaml
from typing import Tuple
from pathlib import Path

from softnanotools.logger import Logger
logger = Logger('GENERATE')

import subprocess

def complete_paths(folders: dict, data: dict) -> dict:
    result = data.copy()
    for key, value in folders.items():
        if key in result.keys():
            if isinstance(result[key], str):
                result[key] = str(Path(value) / result[key])
            elif isinstance(result[key], list):
                temp = []
                for i in result[key]:
                    temp.append(str(Path(value) / i))
                result[key] = temp
                del temp
            elif isinstance(result[key], dict):
                for _key, _value in result[key].items():
                    result[key][_key] = str(Path(value) / result[key][_key])
            else:
                raise TypeError(f'Issue with folder: {key} ... \n{result[key]}')
    logger.debug(f'Changed {json.dumps(data, indent=2)} to {json.dumps(result, indent=2)}')
    return result

def parse_yaml(fyaml: str) -> Tuple[dict]:
    with open(fyaml, 'r') as f:
        data = yaml.safe_load(f)
    init = data['initial']
    simu = data['simulation']
    main = data['main']
    programs = data['programs']

    folders = data.get('folders', None)
    if folders:
        for folder in folders.values():
            Path(folder).mkdir(exist_ok=True, parents=True)
        init = complete_paths(folders, init)
        simu = complete_paths(folders, simu)
        main = complete_paths(folders, main)
        programs = complete_paths(folders, programs)
    return (init, simu, main, programs)

def generate_initial_topology(fname: str, N: int, X: int):
    """Writes a simple file with N and X as the total number
    of particles and number of crosslinkers to an oxDNA
    readable topology file"""
    with open(fname, 'w') as f:
        f.write(f'{N} {X}\n')
    logger.debug(f'Written Initial topology to {fname}')
    return

def parse_micro_csd(data: dict) -> Tuple[str, str]:

    if isinstance(data, str):
        try:
            subprocess.check_output(data)
        except subprocess.CalledProcessError:
            logger.debug('Caught Error from micro_csd existing and launching')
            micro_csd_binary = data
        except FileNotFoundError:
            micro_csd_path = data
            micro_csd_binary = compile_micro_csd(micro_csd_path)

    elif isinstance(data, dict):
        keys = data.keys()
        if 'bin' in keys:
            micro_csd_binary = data['bin']

        elif 'cpp' in keys:
            micro_csd_path = data['cpp']
            micro_csd_binary = compile_micro_csd(micro_csd_path)

        else:
            raise TypeError(
                'programs: micro_csd is a dict but has '
                'the wrong keys, it must have either '
                'bin: or cpp: pointing to a compiled '
                'program or cpp file'
            )
    else:
        raise TypeError('Incorrect entry for micro_csd')

    return micro_csd_binary

def compile_micro_csd(path: str, binary: str, compiler: str = 'g++'):
    """Compiles micro_csd.cpp"""
    subprocess.check_output([
        compiler,
        '-o',
        binary
    ])

def main(setup_yaml: str):
    # get filenames
    init, simu, main, programs = parse_yaml(setup_yaml)

    N = int(init['N'])
    box = float(init['box'])
    crosslinker = init['crosslinker']
    if isinstance(crosslinker, dict):
        crosslinker_ratio = crosslinker.get('ratio', 0.0)
        crosslinker_amount = crosslinker.get('amount', 0)
    else:
        crosslinker = float(crosslinker)
        if crosslinker < 1.0:
            crosslinker_amount = 0
            crosslinker_ratio = crosslinker
        elif crosslinker > 1.0:
            crosslinker_amount = int(crosslinker)
            crosslinker_ratio = 0.0

    logger.debug(
        f'Input Arguments:\n\t'
        f'N:\t{N}\n\t'
        f'X-Frac:\t{crosslinker_ratio}\n\t'
        f'X-No.:\t{crosslinker_amount}'
    )

    if crosslinker_amount and crosslinker_ratio:
        raise TypeError(
            f'Do not set crosslinker_amount ({crosslinker_amount})'
            f' and crosslinker_ratio ({crosslinker_ratio})'
        )

    if crosslinker_ratio:
        crosslinker_amount = int(crosslinker_ratio * N)

    elif crosslinker_amount:
        pass

    else:
        raise TypeError(
            f'Please set either crosslinker_amount ({crosslinker_amount})'
            f' or crosslinker_ratio ({crosslinker_ratio})'
        )

    logger.info(
        f'Generating Gel with:\n\t'
        f'Total Particles:\t{N}\n\t'
        f'No. of Crosslinkers:\t{crosslinker_amount}'
    )

    # create topology file
    generate_initial_topology(init['topology'], N, crosslinker_amount)

    if simu['forces']:
        forces = True
        forces_file = simu['forces']
        with open(forces_file, 'w') as f:
            f.write(json.dumps({
                'type': 'sphere',
                'stiff': 3.0,
                'r0': str(box / 2),
                'center' : ','.join([str(box/2)] * 3),
                'particle': -1
            }, indent=2, separators=('', ' = ')).replace('"', ''))
    else:
        forces = False
        forces_file = '_'


    # Use confGenerator to generate configuration

    small_box = (np.sqrt(3)/4) * box
    logger.debug(f'Using small-box size for generation: {small_box}')
    with open(init['screen'], 'w') as f:
        subprocess.check_output([
            (Path(programs['oxDNA']) / 'build' / 'bin' / 'confGenerator').resolve(),
            init['input_file'],
            str(small_box),
            f"topology={init['topology']}",
            f"conf_file={init['configuration']}",
            f"plugin_search_path={programs['oxDNA']}/contrib/rovigatti",
            f"external_forces={forces}",
            f"external_forces_file={forces_file}",
        ], stderr=f)

    with open(init['configuration'], 'r') as f:
        data = f.readlines()

    data[1] = f"b = {box} {box} {box}\n"
    with open(init['configuration'], 'w') as f:
        f.write(''.join(data))

    logger.info(f"Finished Running confGenerator -> see log at {init['screen']}")

       # Use oxDNA to run a simulation
    temperature = simu.get('T', 0.05)
    try:
        with open(simu['screen'], 'w') as f:
            logger.info(
                f"Running oxDNA (this may take a while) - "
                "Use Ctrl+C to exit simulation\n"
                "Track simulation progress at energy.dat"
            )
            subprocess.check_output([
                (Path(programs['oxDNA']) / 'build' / 'bin' / 'oxDNA').resolve(),
                simu['input_file'],
                f"topology={init['topology']}",
                f"conf_file={init['configuration']}",
                f"print_conf_interval={simu['interval']}",
                f"print_energy_every={simu['interval']}",
                f"steps={simu['steps']}",
                f"trajectory_file={simu['trajectory']}",
                f"seed={simu['seed']}",
                f"external_forces={str(forces).lower()}",
                f"external_forces_file={forces_file}",
                f"energy_file={simu['energy']}",
                f"plugin_search_path={programs['oxDNA']}/contrib/rovigatti",
                f"T={temperature}"
            ], stderr=f)
    except KeyboardInterrupt:
        logger.debug('Caught KeyboardInterrupt whilst running oxDNA and not exiting')

    logger.info(f"Finished Running oxDNA -> see log at {simu['screen']}")

    # reorganise files
    Path('bonds.dat').rename(init['bonds'])
    Path('last_backup.dat').rename(simu['last'])

    # Use microCSD to do cluster analysis
    micro_csd_binary = parse_micro_csd(programs['micro_csd'])
    subprocess.check_output([
        micro_csd_binary,
        init['bonds'],
        init['topology'],
        simu['last']
    ])

    # Use DNAnalysis to create the main files
    with open(main['screen'], 'w') as f:
        subprocess.check_output([
            (Path(programs['oxDNA']) / 'build' / 'bin' / 'DNAnalysis').resolve(),
            main['input_file'],
            f"conf_file={init['configuration']}",
            f"plugin_search_path={programs['oxDNA']}/contrib/rovigatti"
        ], stderr=f)
    logger.info(f"Finished Running DNAnalysis -> see log at {main['screen']}")

    Path('largest_topology.dat').rename(main['topology'])
    Path('largest_bonds.dat').rename(main['configuration'])
    Path('nico_bonds.dat').rename(main['bonds'])
    Path('last_conf.dat').unlink()
    Path('with_patches.dat').unlink()

    logger.info(f"Finished Generation!")

    return

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('setup_yaml')
    main(**vars(parser.parse_args()))
