import yaml

from softnanotools.logger import Logger
logger = Logger(__name__)

from parse import read_settings # type: ignore

def main(**kwargs):
    logger.info('Running...')
    read_settings(kwargs)
    return

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('settings')
    with open(parser.parse_args().settings, 'r') as f:
        settings = yaml.safe_load(f)
    main(**settings)