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
    
    system = EnzymaticDegradation(
        [10., 10., 10.],
        diffusion_constant=1.0, 
        sigma=1.0, 
        epsilon=1.0, 
        cutoff=1.0
    )
    gel = generate_gel()
    system.insert_topology(gel, diffusion_constant=1.0)
    gel.register_decay(system)
    system.add_enzyme(np.array([[5.0, 0.0, 0.0]]))
    simulation = system.initialise_simulation()
    simulation.run(10, 0.1)
    return

def test_degradation_payload():
    system = EnzymaticDegradation(
        [10., 10., 10.],
        diffusion_constant=1.0, 
        sigma=1.0, 
        epsilon=1.0, 
        cutoff=1.0
    )
    gel = generate_gel()
    system.insert_topology(gel, diffusion_constant=1.0)
    gel.register_decay(system)
    system.add_enzyme(np.array([[5.0, 0.0, 0.0]]))
    system.add_payload(np.array([[3.0, 0.0, 0.0]]))
    simulation = system.initialise_simulation()
    simulation.run(10, 0.1)
    return

if __name__ == '__main__':
    test_degradation()
    test_degradation_payload()