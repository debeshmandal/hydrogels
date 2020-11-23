import numpy as np
import os

import pytest

@pytest.mark.skip
def test_polymer_system():
    # do imports
    from hydrogels.generators.polymers import LinearPolymer
    from hydrogels import System

    # initialise system
    system = System(np.array([50., 50., 50.]))

    # add polymers to system
    top_type = 'polymer'
    for i in range(10):
        # create polymer
        polymer = LinearPolymer(top_type, 5, start=np.array([float(i), 0., 0.]))
        # add to system/simulation
        system.insert_topology(polymer, diffusion_constant=1.0)
        
        # add bonds
        system.topologies.configure_harmonic_bond('head', 'core', force_constant=70., length=1.5)
        system.topologies.configure_harmonic_bond('core', 'core', force_constant=70., length=1.5)

        # add repulsive potential
        system.potentials.add_harmonic_repulsion('core', 'core', force_constant=70., interaction_distance=2.0)
        system.potentials.add_harmonic_repulsion('head', 'head', force_constant=70., interaction_distance=2.0)
        system.potentials.add_harmonic_repulsion('core', 'head', force_constant=70., interaction_distance=2.0) 

    # run simulation
    simulation = system.initialise_simulation()
    simulation.run(10, 0.1)
    os.remove(simulation.output_file)


if __name__ == '__main__':
    test_polymer_system()
