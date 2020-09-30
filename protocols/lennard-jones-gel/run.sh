path=~/hydrogels/protocols/lennard-jones-gel
folder=.

BOX=50.0
DT=0.001
LJEPS=0.0
LJSIG=1.0
LJCUT=5.0

python $path/main.py \
	--box $BOX \
	--stride 1 \
	--length 100 \
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

python $path/trajectory.py _out.h5 \
	--show \
	--particles-file $folder/particles.csv \
	--plot-file $folder/particles.pdf \
	--traj-folder $folder/traj \
	--json $folder/simulation.json

exit 1 

python $path/model.py $folder/simulation.json

mv _out.* $folder
