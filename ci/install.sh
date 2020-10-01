echo "Installing HDF5"
HDF5_VERSION=1.12.0
pushd /tmp
wget "https://www.hdfgroup.org/ftp/HDF5/releases/hdf5-${HDF5_VERSION%.*}/hdf5-$HDF5_VERSION/src/hdf5-$HDF5_VERSION.tar.gz"
tar -xzf hdf5-$HDF5_VERSION.tar.gz
pushd hdf5-$HDF5_VERSION
chmod u+x autogen.sh
source configure
make -j $(nproc)
sudo make install
popd
popd

pip3 install --upgrade pip setuptools wheel
pip3 install numpy
pip3 install scipy
pip3 install pandas
pip3 install matplotlib

pip3 install "pybind11[global]"
pip3 install h5py

git clone https://github.com/readdy/readdy
pip3 install ./readdy

pip3 install .

pip3 install cibuildwheel==1.6.1