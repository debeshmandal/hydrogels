import numpy as np
from hydrogels.generators.gels import LennardJonesGel
import readdy

gel = LennardJonesGel(
    np.array([30., 30., 30.]),
    N = 50,
    R = 5,
    bond_strength = 5.0,
    bond_length = 0.5,
    lj_eps = 2.0,
    lj_sig = 1.0,
    lj_cutoff = 5.0,
    diffusion_constant=0.1
)
spatial_reaction = f'reaction: {gel.top_type}({gel.monomer})+(enzyme) -> {gel.top_type}({gel.unbonded})+(enzyme)'
gel.topologies.configure_harmonic_bond('unbonded', 'monomer', force_constant=0., length=1.)
gel.add_enzyme(
    np.array([
        [20., 20., 20.],
        [10., 10., 10.],
        [15., 15., 15.],
        [12.5, 15., 20.],
        [15., 12.5, 12.5],
        [20., 22., 20.],
        [10., 12., 10.],
        [15., 12., 15.],
        [12.5, 12., 20.],
        [15., 11, 12.5],
        [15., 12.5, 12.5],
        [10., 22., 20.],
        [12., 12., 10.],
        [12., 12., 15.],
        [12, 12., 20.],
        [12., 11, 12.5],
    ]) - 5.0, 
    epsilon=1.0, 
    sigma=1.0,
    spatial_reaction=spatial_reaction,
    rate=5.0,
    radius=2.0
)
gel.add_species('released', 1.0)
gel._species.append('released')

def reaction_function(topology):
    recipe = readdy.StructuralReactionRecipe(topology)
    index = np.random.randint(0, len(topology.particles))
    if topology.particles[index].type == 'unbonded':
        recipe.separate_vertex(index)
        recipe.change_particle_type(index, "released")
    return recipe

gel.topologies.add_structural_reaction(
    'decay',
    topology_type='lj-gel',
    reaction_function=reaction_function,
    rate_function = lambda x: 1e2)

for particle in gel._species:
    gel.potentials.add_sphere(
        particle_type=particle, force_constant=10., origin=[0, 0, 0], radius=15., inclusion=True
    )

simu = gel.initialise_simulation()
stride = 1000
simu.observe.topologies(stride)
simu.record_trajectory(stride)
simu.run(500 * stride, 0.005)
