# oxDNA Gel Generation

## Summary

In this protocol, oxDNA is used to generate crosslinked gel networks. It does this by implementing patchy particle potentials.

Four files are outputted:

- CSV: table containing edges with positional information that can be extracted
- BILD: viewable by UCSF Chimera
- XYZ: simple XYZ positions
- LAMMPS: LAMMPS data file

## Usage

The `settings.yml` file can be customised to set up filenames and parameters. Once this has been set up. The script can access it by doing:

```
python main.py settings.yml
```

We recommend tarballing the main files and copying them to an active location. When doing many simulation in parallel, it is important to call the oxDNA executables from different directories and tarballing the main files makes this easier. The Python scripts are small and can be copied very quickly when tarballed. The tarballing process is also quick related to the time required to run the simulation.

For example:
```sh
WORKDIR=/path/to/working_directory/
tar czf gel.tar.gz analyze convert generate main.py settings.yml
mkdir -p $WORKDIR
cp gel.tar.gz $WORKDIR
cd $WORKDIR
tar xzf gel.tar.gz
python main.py settings.yml
```

The oxDNA bonds file is needed to do the conversion to more useful file formats. The `convert` area of the code is where this takes place.

Since the naming of files is often done within Python, this has been omitted from `settings.yml`. The file naming conventions are stored in `main.py` where a folder called `configs` and files that follow the pattern `gel-N{N}-X{amount}-b{int(box)}.{seed}` are created. This can be edited by the user manually.

## YAML Schema

```yaml
folders: 
  crosslinker: all crosslinker files will be in 
               this folder, the program will 
               search through each entry in folders 
               and then change the filename 
               to folder/filename
  topology: same as above but for topology entries
  bonds: same as above
  etc: ...
  
initial:
  box: cubic box length
  N: total number of particles
  crosslinker: no. of crosslinker particles if > 1.0 
               or fraction if less than
  configuration: name of initial configuration file
  topology: name of initial topology file
  bonds: name of initial bonds file
  input_file: name of confGenerator input file
  seed: random seed
  screen: logging file

simulation:
  trajectory: simulation trajectory
  last: last configuration of simulation
  energy: energy filename
  input_file: name of oxDNA input file
  seed: random seed
  interval: printing energy and configuration interval
  steps: number of simulation steps
  screen: logging file
  forces: external forces (optional)

main:
  configuration: final configuration file
  topology: final topology file
  bonds: final bonds file
  input_file: input file for DNAnalysis
  screen: logging file

programs:
  oxDNA: path to oxDNA executable
  DNAnalysis: path to DNAnalysis executable
  confGenerator: path to confGenerator executable
  micro_csd: 
    bin: path to micro_csd executable
    cpp: path to micro_csd.cpp 
  compiler: c++ compiler (usually g++)
```