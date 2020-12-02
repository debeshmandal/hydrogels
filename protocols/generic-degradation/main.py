import json

from softnanotools.logger import Logger
logger = Logger('main')

import simulation.main as simulate

def main(**kwargs):
    logger.debug(f'Using settings:\n{json.dumps(kwargs, indent=2)}')
    return

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    main(**vars(parser.parse_args()))