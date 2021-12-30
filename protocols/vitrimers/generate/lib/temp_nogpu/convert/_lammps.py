import pandas as pd
import time
import numpy as np

def write(
    fname: str, 
    particles: pd.DataFrame, 
    edges: pd.DataFrame, 
    box: np.ndarray):
    with open(fname, 'w') as f:
        f.write(f'# oxDNA Generated Gel - Generated on {time.ctime()}\n\n')
        f.write(f'{len(particles)} atoms\n')
        f.write(f'{len(edges)} bonds\n\n')
        _atom_types = len(np.unique(particles["crosslinker"].to_numpy()))
        f.write(f'{_atom_types} atom types\n')
        f.write(f'1 bond types\n\n')
        f.write(f'-{box[0]} {box[0]} xlo xhi\n')
        f.write(f'-{box[1]} {box[1]} ylo yhi\n')
        f.write(f'-{box[2]} {box[2]} zlo zhi\n\n')
        f.write('Masses\n\n')
        f.write('\n'.join([f'{i+1} 1.0' for i in range(_atom_types)]))
        f.write('\n\nAtoms\n\n')
        temp = particles.copy()
        temp['id'] = range(1, len(particles)+1)
        temp['mol'] = len(particles) * [1]
        temp['type'] = temp['crosslinker'].apply(lambda x: int(x) + 1)
        temp['q'] = len(particles) * [0]
        temp[['id', 'mol', 'type', 'x', 'y', 'z']].to_csv(f, sep=' ', index=False, header=False)
        f.write('\n\nBonds\n\n')
        temp = edges.copy()
        temp['id'] = range(1, len(temp)+1)
        temp['type'] = len(temp) * [1]
        temp[['id', 'type', 'atom_1', 'atom_2']].to_csv(f, sep=' ', index=False, header=False)

    return
