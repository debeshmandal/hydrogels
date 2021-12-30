import pandas as pd
import numpy as np

from typing import List

from softnanotools.logger import Logger
logger = Logger('BILD')

def write(
    fname: str,
    particles: pd.DataFrame,
    edges: List[list],
    _box: np.ndarray,
    *args
):
    box = _box[0]
    if any(edges['length'] > box / 2):
        logger.warning(f'Some edges are longer than {box / 2}:\n{edges[edges["length"] > (box / 2)]}')

    with open(fname, 'w') as f:
        f.write('.comment -- oxDNA gel generation visualisation\n')
        f.write('.comment -- Draw crosslinkers\n')
        f.write('.color red\n')
        temp = particles[particles['crosslinker']]
        temp[['bild-cmd', 'x', 'y', 'z', 'r']].to_csv(
            f, sep=' ', index=False, header=None
        )
        f.write('.comment -- Draw particles\n')
        f.write('.color white\n')
        temp = particles[~particles['crosslinker']]
        temp[['bild-cmd', 'x', 'y', 'z', 'r']].to_csv(
            f, sep=' ', index=False, header=None
        )
        f.write('.comment -- Draw edges\n')
        edges[['bild-cmd', 'x1', 'y1', 'z1', 'x2', 'y2', 'z2']].to_csv(
            f, sep=' ', index=False, header=None
        )
