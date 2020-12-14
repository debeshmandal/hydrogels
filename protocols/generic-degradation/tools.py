import yaml
import json

from softnanotools.logger import Logger
logger = Logger('tools')

def parse_yaml(fname: str):
    with open(fname, 'r') as f:
        data = yaml.safe_load(f)
    logger.debug(
        f'Loaded data:\n{json.dumps(data, indent=2)}'
    )
    return data