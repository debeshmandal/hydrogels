pip3 install --upgrade pip setuptools wheel
pip3 install numpy
pip3 install scipy
pip3 install pandas
pip3 install matplotlib
pip3 install tqdm

pip3 install pybind11
pip3 install h5py

pushd /tmp
git clone https://github.com/readdy/readdy
pushd readdy
pip3 install .
popd
popd

# install hydrogels
pip3 install .

pip3 install cibuildwheel==1.6.1