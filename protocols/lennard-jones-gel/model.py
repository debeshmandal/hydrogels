#!/usr/bin/env python

def _model():
    return

def main(**kwargs):
    folder = kwargs.get('traj_folder')
    prefix = kwargs.get('prefix')

    model = _model(**kwargs)

    return

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()

    parser.add_argument('traj-folder')
    parser.add_argument('--prefix', required=False, default='traj.xyz.{}')

    args = vars(parser.parse_args())
    main(**args)