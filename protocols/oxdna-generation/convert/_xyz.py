import pandas as pd
import numpy as np

def write(fname, particles, *args):
    with open(fname, 'w') as f:
        particles['t'] = particles['crosslinker'].apply(lambda x: int(x) + 1)
        f.write(f'{len(particles)}\n\n')
        particles[['t', 'x', 'y', 'z']].to_csv(f, sep='\t', index=False, header=False)