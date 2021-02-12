import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import readdy

from model import read_lammps_conf # type: ignore

data = read_lammps_conf('data.out')
edges = data['edges'][['atom_1', 'atom_2']]


positions = data['particles'].sort_values(by='id')
print(positions)

def r(ID: int):
    return positions[positions['id']==ID][['x', 'y', 'z']].to_numpy()

def length(atom_1: int, atom_2: int):
    pos_1 = r(atom_1)
    pos_2 = r(atom_2)
    return np.linalg.norm(pos_1 - pos_2)

edges['length'] = edges.apply(lambda x: length(x['atom_1'], x['atom_2']), axis=1)

traj = readdy.Trajectory('_out.h5').read()

def readdy_position(ID: int, frame: int):
    return traj[frame][ID].position

test_pos = readdy_position(1500, 0)

for i in range(len(positions)):
    pos = positions.loc[i]
    if test_pos[0] == pos['x']:
        print(i, pos['x'])
    if test_pos[1] == pos['y']:
        print(i, pos['y'])
    if test_pos[2] == pos['z']:
        print(i, pos['z'])
