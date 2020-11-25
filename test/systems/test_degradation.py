import numpy as np

from hydrogels.systems import EnzymaticDegradation
from hydrogels.generators.gels import Gel

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

def test_degradation():
    gel = generate_gel()
    system = EnzymaticDegradation([10., 10., 10.])
    system.insert_topology(gel, diffusion_constant=1.0)
    system.add_enzyme()
    simulation = system.initialise_simulation()
    simulation.run(10, 0.1)
    return

def test_degradation_payload():
    gel = generate_gel()
    system = EnzymaticDegradation([10., 10., 10.])
    system.insert_topology(gel, diffusion_constant=1.0)
    system.add_enzyme()
    system.add_payload()
    simulation = system.initialise_simulation()
    simulation.run(10, 0.1)
    return

if __name__ == '__main__':
    test_degradation()
    test_degradation_payload()