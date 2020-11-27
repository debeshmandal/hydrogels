from hydrogels.generators.gels import Gel

from hydrogels.utils.system import System

import numpy as np

def generate_gel():
    """Generates a gel"""
    gel = Gel(
        'gel',
        np.array([
            [1., 0., 0.],
            [1., 1., 0.],
            [0., 1., 0.],
            [0., 0., 0.],
        ]) 
    )
    gel.edges = [
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 2),
        (1, 3),
        (2, 3),
    ]
    gel.configure_bonds('harmonic', force_constant=1.0, length=1.0)
    return gel

def test_Gel():
    gel = generate_gel()
    system = System([10., 10., 10.])
    system.insert_topology(gel, diffusion_constant=1.0)
    simulation = system.initialise_simulation()
    simulation.run(10, 0.1)
    return

if __name__ == '__main__':
    test_Gel()