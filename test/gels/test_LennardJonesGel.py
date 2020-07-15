import pytest 
import numpy as np

def test_LennardJonesGel_generation():
    from hydrogels.generators.gels import LennardJonesGel
    gel = LennardJonesGel(
        np.array([50., 50., 50.]),
        N = 100,
        R = 10,
        bond_strength = 10.0,
        bond_length = 1.5,
        lj_eps = 1.0,
        lj_sig = 1.0,
        lj_cutoff = 10.0,
        diffusion_constant=1.0
    )
    spatial_reaction = f'reaction: {gel.top_type}({gel.monomer})+(enzyme) -> {gel.top_type}({gel.unbonded})+(enzyme)'
    gel.add_enzyme(
        np.array([[20., 20., 20.]]), 
        epsilon=1.0, 
        sigma=1.0,
        spatial_reaction=spatial_reaction,
        rate=5.0,
        radius=2.0
    )
    simu = gel.initialise_simulation()
    simu.run(10, 0.1)
    return