# Vitrimers

## Summary

A full end-to-end set of scripts that utilise three simulations softwares oxDNA, LAMMPS, and ReaDDy
to generate realistic microgel networks using swap-driven dynamics, equilibrate them using Langevin
dynamics and perform enzymatic degradation using interparticular reaction dynamics (iPRD).

## Structure

There are three directories, each self-contained per protocol that each have the same, or similar
structure:

```
.
├── Dockerfile
├── README.md
├── lib
│   ├── main.py
│   ├── ...
│   ├── ...
└── settings.yml
```

### `Dockerfile`

A Dockerfile for use with Docker or Singularity (this is useful for non-root users e.g. all
scientists working on university clusters). In the future, `hydrogels` will have Docker
functionality built in the core package.

### `README.md`

A description of the protocol and a detailed description of the options found in `settings.yml`

### `lib`

The backend for the protocol access through the entrypoint `lib/main.py`

### `settings.yml`

A YAML formatted configuration file that is typically the only mandatory argument for
`lib/main.py`. The use of this file format as opposed to JSON is due to its ability to be edited
manually or scripted using the `pyyaml` Python package.

## PBS, SLURM, Docker

Each of the solutions contains a file `initialise_*.sh` which sets up the protocols for use with
that particular setup.

### HPC

For PBS and SLURM, a set of scripts are generated that provide variables at the top of the script.
The choice settings (i.e. `#PBS -J 1-10`) are driven by the authors working environments. We are
open to expanding the scripts and presets in the future, please create a pull request with your
new configuration.

### Containers

For Docker and Singularity, the shell scripts are provided to build the containers, typically this
enters each of the folders and calls a build function and tags the containers with
`hydrogels/vitrimers-*` where `*` is replaced by the name of the protocol. The containers can then
be run within the directory (or volume) where a user may want to store their files.
