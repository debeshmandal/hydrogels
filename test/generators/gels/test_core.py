from hydrogels.generators.gels import Gel

from hydrogels.utils.system import System

import numpy as np

def generate_gel():
    """Generates a gel"""
    gel = Gel('gel')
    gel.positions = np.array([
        [1., 0., 0.],
        [1., 1., 0.],
        [0., 1., 0.],
        [0., 0., 0.],
    ])
    gel.sequence = len(gel.positions) * ['monomer']
    gel.edges = [
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 2),
        (1, 3),
        (2, 3),
    ]
    gel.add_bond(
        'harmonic', 
        'monomer', 
        'monomer', 
        force_constant=1.0,
        length=1.0
    )
    return gel

def generate_system():
    """Generates a system"""
    return System([10., 10., 10.])

def test_Gel():
    gel = generate_gel()
    system = generate_system()
    system.insert_topology(gel, diffusion_constant=1.0)
    simulation = system.initialise_simulation()
    simulation.run(10, 0.1)
    return

def test_Gel_drug():
    gel = generate_gel()
    system = generate_system()
    system.insert_topology(gel, diffusion_constant=1.0)
    system.insert_species(
        'drug', 
        1.0, 
        np.array([
            [0.25, 0.25, 0.],
            [0.5, 0.25, 0.],
            [0.5, 0.5, 0.],
            [0.25, 0.5, 0.],
        ])
    )
    simulation = system.initialise_simulation()
    simulation.run(10, 0.1)
    return

def test_Gel_enzyme():
    gel = generate_gel()
    system = generate_system()
    system.insert_topology(gel, diffusion_constant=1.0)
    system.insert_species(
        'enzyme', 
        1.0, 
        np.array([
            [0.25, 0.25, 0.],
            [0.5, 0.25, 0.],
            [0.5, 0.5, 0.],
            [0.25, 0.5, 0.],
        ])
    )
    simulation = system.initialise_simulation()
    simulation.run(10, 0.1)
    return

def test_Gel_drug_enzyme():
    return

if __name__ == '__main__':
    test_Gel()
    test_Gel_enzyme()
    test_Gel_drug()
    test_Gel_drug_enzyme()