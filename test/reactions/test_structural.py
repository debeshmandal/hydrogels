#!/usr/bin/env python
"""
pytest script for testing utils folder
"""
from math import comb
from pathlib import Path
import numpy as np

from hydrogels import System, Topology
from hydrogels.utils.topology import TopologyBond
from hydrogels.reactions import BondBreaking
from hydrogels.trajectory.core import ParticleTrajectory

from pathlib import Path

from softnanotools.logger import Logger
logger = Logger(__name__)

FOLDER = Path(__file__).parent
OUTPUT = FOLDER / '_out.h5'

def test_diatomic():
    system = System([10., 10., 10.])
    topology = Topology(
        'molecule',
        sequence = ['A', 'B'],
        positions = np.array([
            [0., 0., 0.],
            [1., 0., 0.]
        ]),
        edges = [(0, 1)]
    )
    reaction_container = BondBreaking('A', 'B', 'C')

    system.topologies.add_type('molecule')
    system.add_topology_species('A', 1.0)
    system.add_topology_species('B', 1.0)
    system.add_species('C', 1.0)

    for combination in (
        ['A', 'A'],
        ['A', 'B'],
        ['B', 'B']
    ):
        TopologyBond(
            'harmonic',
            combination[0],
            combination[1],
            force_constant=1.0,
            length=1.0,
        ).register(system)


    system.topologies.add_structural_reaction(
        name=reaction_container.name,
        topology_type=reaction_container.topology_type,
        reaction_function=reaction_container.diatomic,
        rate_function=reaction_container.rate_function,
    )

    if OUTPUT.exists():
        OUTPUT.unlink()
    simulation = system.simulation(output_file=str(OUTPUT.absolute()))
    simulation.reaction_handler = 'Gillespie'

    topology.add_to_sim(simulation)
    stride = 1
    simulation.record_trajectory(stride)
    simulation.observe.particles(stride)
    simulation.run(10, 0.1)

    # check that only 2 C atoms are present
    trajectory = ParticleTrajectory(OUTPUT)
    frame = trajectory.frames[-1]
    assert list(frame.dataframe['type']) == ['C', 'C']

    OUTPUT.unlink()
    return

def test_polymer():
    system = System([10., 10., 10.])
    topology = Topology(
        'molecule',
        sequence = ['A', 'B', 'A', 'A'],
        positions = np.array([
            [0., 0., 0.],
            [1., 0., 0.],
            [2., 0., 0.],
            [3., 0., 0.],
        ]),
        edges = [(0, 1), (1, 2), (2, 3)]
    )
    reaction_container = BondBreaking('A', 'B', 'C')

    system.topologies.add_type('molecule')
    system.add_topology_species('A', 1.0)
    system.add_topology_species('B', 1.0)
    system.add_species('C', 1.0)

    for combination in (
        ['A', 'A'],
        ['A', 'B'],
        ['B', 'B']
    ):
        TopologyBond(
            'harmonic',
            combination[0],
            combination[1],
            force_constant=1.0,
            length=1.0,
        ).register(system)


    system.topologies.add_structural_reaction(
        name=reaction_container.name,
        topology_type=reaction_container.topology_type,
        reaction_function=reaction_container.polymer,
        rate_function=reaction_container.rate_function,
    )

    if OUTPUT.exists():
        OUTPUT.unlink()
    simulation = system.simulation(output_file=str(OUTPUT.absolute()))
    simulation.reaction_handler = 'Gillespie'

    topology.add_to_sim(simulation)
    stride = 1
    simulation.record_trajectory(stride)
    simulation.observe.particles(stride)
    simulation.run(10, 0.1)

    # check that only 2 C atoms are present
    trajectory = ParticleTrajectory(OUTPUT)
    frame = trajectory.frames[0]
    logger.info(frame.dataframe)
    frame = trajectory.frames[-1]
    logger.info(frame.dataframe)
    assert sorted(list(frame.dataframe['type'])) == ['A', 'A', 'C', 'C']

    OUTPUT.unlink()
    return

if __name__=='__main__':
    test_diatomic()
    test_polymer()
