#!/usr/bin/bash
path=~/hydrogels/protocols/lennard-jones-gel
folder=.

BOX=50.0
DT=0.001
LJEPS=0.0
LJSIG=1.0
LJCUT=5.0

echo "SCRIPT: Testing main.py..."
python $path/main.py \
	--box $BOX \
	--stride 5000 \
	--length 500 \
	--timestep $DT \
	--number 50 \
	--radius 3.0 \
	--lj-eps $LJEPS \
	--lj-sig $LJSIG \
	--lj-cutoff $LJCUT \
	--bond-strength 1.0 \
	--enzyme-number 100 \
	--enzyme-radius 24.0 \
	--reaction-radius 2.5 \
	--diffusion-constant 5.0 \
	--json $folder/simulation.json

echo "SCRIPT: Testing trajectory.py"
python $path/trajectory.py \
	--fname _out.h5 \
	--particles-file $folder/particles.csv \
	--plot-file $folder/particles.pdf \
	--traj-folder $folder/traj \
	--json $folder/simulation.json

echo "SCRIPT: Testing model.py"
python $path/model.py \
	--json $folder/simulation.json \
	--plot-file $folder/model.png \
	--model-file $folder/model.csv \
	--show
