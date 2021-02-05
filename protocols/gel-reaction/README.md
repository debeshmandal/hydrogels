# Gel Reaction

## Summary

## Usage

To prepare a system use:

```
python prepare.py prepare.yml
```

To simulate the reaction use:

```
python simulation.py settings.yml
```

To convert the trajectory to XYZ use:

```
python trajectory.py _out.h5
```

## `prepare.py` - YAML schema

```yaml
initial: equilibrated gel
final: equilibrated gel with enzyme (and payload if relevant)
input: lammps input file for equilibration
box: [x, y, z] box size
enzyme: number of enzymes
payload: number of payload particles
lammps: lammps command
```

## `simulation.py` - YAML schema

```yaml
reader: options for a Reader object
diffusion_dictionary: dictionary of diffusion constants
bonding: bonds for bonding manager
potentials: parameters for PotentialManager
reaction: reaction parameters
simulation: simulation parameters
```