bash package.sh
mkdir -p run
pushd run
cp ../package.tar.gz .
tar xzf package.tar.gz
cp ../lammps.main.conf .
cp ../checkpoint_100000.h5 .
python main.py settings.yml --checkpoint checkpoint_100000.h5
popd