pip3 install --upgrade pip setuptools wheel
pip3 install numpy
pip3 install scipy
pip3 install pandas
pip3 install matplotlib
pip3 install tqdm

pip3 install pybind11
pip3 install h5py

export HDF5_DIR=/usr/local/HDF_Group/HDF5/1.12.0/share/cmake 
git clone https://github.com/readdy/readdy
pip3 install ./readdy

# install hydrogels
pip3 install .

pip3 install cibuildwheel==1.6.1