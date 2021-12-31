#!/usr/bin/env python
"""Analysis collation tool - uses Writer instances to iterate over many
dump files to produce averages
"""

from pathlib import Path
import yaml

from writer import MicrogelWriter, EnzymeWriter #type: ignore


def main(dump: str, dest: str = None, settings: str = 'settings.yml'):
    writers = {
        'gel': MicrogelWriter(),
        'enzyme': EnzymeWriter()
    }

    with open(settings, 'r') as f:
        data = yaml.safe_load(f)

    for name, writer in writers.items():
        writer.process_files(
            Path(dump).glob(f'dump.{name}.*'),
            bin_width = data['bin_width'],
            box = data['box'],
            potential_settings = data['potential']
        )

    if dest:
        for name, writer in writers.items():
            with open(Path(dest) / f'{dump}.{name}.json', 'w') as f:
                f.write(writer.json)

    return

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('dump', help='Path to dump folder')
    parser.add_argument('--dest', help='destination for results')
    parser.add_argument('-s', '--settings', default='settings.yml')
    main(**vars(parser.parse_args()))
