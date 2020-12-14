import matplotlib.pyplot as plt

import generate
import convert
import analyse
import equilibrate

import yaml
from pathlib import Path


def main(settings: str, run: bool = False):
    if run:
        generate.run(settings)

    with open(settings, 'r') as f:
        params = yaml.safe_load(f)

    N = params['initial']['N']
    box = params['initial']['box']
    amount = params['initial']['crosslinker']
    seed = params['simulation'].get('seed', 1)

    inputs = convert.read(f"{params['folders']['bonds']}/{params['main']['bonds']}")
    Path('configs').mkdir(exist_ok=True, parents=True)
    prefix = f'configs/gel-N{N}-X{amount}-b{int(box)}.{seed}'
    convert.write_bild(f'{prefix}.bild', *inputs)
    convert.write_lammps(f'{prefix}.lammps', *inputs)
    convert.write_xyz(f'{prefix}.xyz', *inputs)
    inputs[1].to_csv(f'{prefix}.csv')
    equilibrate.run_equilibration(f'{prefix}.lammps')
    return

def analysis(inputs):
    model = analyse.Model(*inputs)
    rdf_kwargs = dict(bins=50, range=(0, inputs[2][0]/2))
    rdf = model.rdf(**rdf_kwargs)
    width = 0.8 * (rdf[0][1] - rdf[0][0])
    plt.bar(rdf[0], rdf[1], width=width, alpha=0.2)
    plt.plot(rdf[0], rdf[1], 'x-', label='all')
    rdf = model.rdf(crosslinkers=True, **rdf_kwargs)
    width = 0.8 * (rdf[0][1] - rdf[0][0])
    plt.bar(rdf[0], rdf[1], width=width, alpha=0.2)
    plt.plot(rdf[0], rdf[1], 'x-', label='crosslinkers')
    plt.xlabel('r')
    plt.ylabel('g(r)')
    plt.legend()
    plt.show()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('settings')
    parser.add_argument('--run', action='store_true')
    main(**vars(parser.parse_args()))
