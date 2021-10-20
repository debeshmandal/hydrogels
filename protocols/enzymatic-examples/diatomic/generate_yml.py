#!/usr/bin/env python
"""generate_yml.py.py - auto-generated by softnanotools"""
from softnanotools.logger import Logger
import yaml
logger = Logger('GENERATE YML')

A = {
    1: {'enzymes': 50},
    2: {'enzymes': 100},
    3: {'enzymes': 150},
    4: {'enzymes': 200},
    5: {'enzymes': 250}
}

B = {
    1: {'spring_length': 0.25},
    2: {'spring_length': 0.50},
    3: {'spring_length': 1.00},
    4: {'spring_length': 1.50},
    5: {'spring_length': 2.00},
}

C = {
    1: {'reaction_rate': 0.01},
    2: {'reaction_rate': 0.1},
    3: {'reaction_rate': 1.0},
    4: {'reaction_rate': 10.0},
}

D = {
    1: {
        'diffusion_dictionary': {
            'A': 0.01,
            'B': 0.01,
            'E': 0.01,
            'C': 0.01,
        }
    },
    2: {
        'diffusion_dictionary': {
            'A': 0.1,
            'B': 0.1,
            'E': 0.1,
            'C': 0.1,
        }
    },
    3: {
        'diffusion_dictionary': {
            'A': 1.0,
            'B': 1.0,
            'E': 1.0,
            'C': 1.0,
        }
    },
    4: {
        'diffusion_dictionary': {
            'A': 10.0,
            'B': 10.0,
            'E': 10.0,
            'C': 10.0,
        }
    },
}

def main(**kwargs):
    logger.info('Running generate_yml...')
    # insert code here
    with open('settings.yml', 'r') as f:
        template = yaml.safe_load(f)
    for schema, name in zip(
        [A, B, C, D],
        ['A', 'B', 'C', 'D']
    ):
        for i, parameters in schema.items():
            data = template.copy()
            for key, value in parameters.items():
                data[key] = value
            with open(f'yml/{name}{i}.yml', 'w') as f:
                yaml.dump(data, f)

    logger.info('Done!')
    return

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='generate_yml.py - auto-generated by softnanotools')
    main(**vars(parser.parse_args()))