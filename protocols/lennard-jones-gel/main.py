import numpy as np
from hydrogels.generators.gels import LennardJonesGel
import readdy
import random

def generate_positions(radius_min, radius_max, N, origin):
    """
    Generate positions within a sphere
    """
    V = []
    costheta = []
    phi = []
    volume_min = 4./3. * np.pi * radius_min ** 3
    volume_max = 4./3. * np.pi * radius_max ** 3
    for i in range(N):
        V.append(random.uniform(volume_min, volume_max))
        costheta.append(random.uniform(-1., 1.))
        phi.append(random.uniform(0., 2*np.pi))
    R = np.cbrt(np.array(V) * 0.75 / np.pi)
    theta = np.arccos(costheta)
    array = np.ones((N, 3))
    array[:, 0] = R * np.sin(theta) * np.cos(phi)
    array[:, 1] = R * np.sin(theta) * np.sin(phi)
    array[:, 2] = R * np.cos(theta)
    return array + origin

def generate_enzyme(**kwargs):
    N = kwargs.get('enzyme_number', 20)
    origin = kwargs.get('enzyme_origin', np.array([0., 0., 0.]))
    excluded_radius = kwargs.get('radius', 5.0)
    max_radius = kwargs.get(
        'enyzme_radius', 
        kwargs.get(
            'box', 
            np.array([30., 30., 30.])
        )[0] / 2
    )

    positions = generate_positions(excluded_radius, max_radius, N, origin)

    params = dict(
        epsilon=kwargs.get('lj_eps', 2.0), 
        sigma=kwargs.get('lj_sig', 1.0),
        rate=kwargs.get('reaction_rate', 100.0),
        radius=kwargs.get('reaction_radius', 2.0)
    )

    print(positions)
    return positions, params

def generate_gel(**kwargs):
    box = kwargs.get('box', np.array([30., 30., 30.]))
    number = kwargs.get('number', 50)
    radius = kwargs.get('radius', 5)
    bond_strength = kwargs.get('bond_strength', 5.0)
    bond_length = kwargs.get('bond_length', 0.5)
    lj_eps = kwargs.get('lj_eps', 2.0)
    lj_sig = kwargs.get('lj_sig', 1.0)
    lj_cutoff = kwargs.get('lj_cutoff', 5.0)
    diffusion_constant = kwargs.get('diffusion_constant', 0.1)

    print(f'Number: {number}, Radius: {radius}')

    gel = LennardJonesGel(
        box,
        N = number,
        R = radius,
        bond_strength = bond_strength,
        bond_length = bond_length,
        lj_eps = lj_eps,
        lj_sig = lj_sig,
        lj_cutoff = lj_cutoff,
        diffusion_constant=diffusion_constant
    )

    spatial_reaction = f'reaction: {gel.top_type}({gel.monomer})+(enzyme) -> {gel.top_type}({gel.unbonded})+(enzyme)'
    gel.topologies.configure_harmonic_bond(
        'unbonded', 
        'monomer', 
        force_constant=0., 
        length=1.
    )
    gel.topologies.configure_harmonic_bond(
        'unbonded', 
        'unbonded', 
        force_constant=0., 
        length=1.
    )
    gel.add_species('released', diffusion_constant)
    gel._species.append('released')

    positions, enzyme_kwargs = generate_enzyme(**kwargs)
    gel.add_enzyme(positions, spatial_reaction=spatial_reaction, **enzyme_kwargs)

    gel.topologies.add_structural_reaction(
        'decay',
        topology_type='lj-gel',
        reaction_function=reaction_function,
        rate_function = lambda x: 1e3)

    sphere_force_constant = kwargs.get('sphere_force_constant', 10.)
    sphere_radius = kwargs.get('sphere_radius', 15.)

    if (sphere_force_constant > 0) and (sphere_radius > 0):
        for particle in gel._species:
            gel.potentials.add_sphere(
                particle_type=particle, 
                force_constant=sphere_force_constant, 
                origin=[0, 0, 0], 
                radius=sphere_radius, 
                inclusion=True
            )
    
    return gel

def run(gel, **kwargs):
    stride = kwargs.get('stride', 1000)
    length = kwargs.get('length', 100)
    timestep = kwargs.get('timestep', 0.001)

    simu = gel.initialise_simulation()
    simu.observe.topologies(stride)
    simu.observe.particles(stride)
    simu.record_trajectory(stride)
    simu.run(length * stride, timestep)

def reaction_function(topology):
    recipe = readdy.StructuralReactionRecipe(topology)
    index = np.random.randint(0, len(topology.particles))
    if topology.particles[index].type == 'unbonded':
        recipe.separate_vertex(index)
        recipe.change_particle_type(index, "released")
    return recipe

def main(**kwargs):
    gel = generate_gel(**kwargs)
    run(gel, **kwargs)

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()

    # gel kwargs
    parser.add_argument('--box', required=False, type=float, default=30.)
    parser.add_argument('--number', required=False, type=int, default=50)
    parser.add_argument('--radius', required=False, type=float, default=5.)
    parser.add_argument('--bond-strength', required=False, type=float, default=2.0)
    parser.add_argument('--bond-length', required=False, type=float, default=2.0)
    parser.add_argument('--lj-eps', required=False, type=float, default=1.0)
    parser.add_argument('--lj-sig', required=False, type=float, default=1.0)
    parser.add_argument('--lj-cutoff', required=False, type=float, default=5.0)
    parser.add_argument('--diffusion-constant', required=False, type=float, default=1.0)

    # enzyme kwargs
    parser.add_argument('--enzyme-number', required=False, type=int, default=10)
    parser.add_argument('--enzyme-radius', required=False, type=float, default=30.)
    parser.add_argument('--reaction-rate', required=False, type=float, default=1000.)
    parser.add_argument('--reaction-radius', required=False, type=float, default=2.0)

    # sphere kwargs
    parser.add_argument('--sphere-radius', required=False, type=float, default=0.)
    parser.add_argument('--sphere-force_constant', required=False, type=float, default=0.0)

    # run kwargs
    parser.add_argument('--stride', required=False, type=int, default=1000)
    parser.add_argument('--timestep', required=False, type=float, default=0.001)
    parser.add_argument('--length', required=False, type=int, default=100)
    args = vars(parser.parse_args())
    if args.get('box', False):
        box = args['box']
        args['box'] = np.array([box, box, box])
    main(**args)
