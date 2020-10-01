pip3 install --upgrade pip setuptools wheel
pip3 install numpy
pip3 install scipy
pip3 install pandas
pip3 install matplotlib

pip3 install "pybind11[global]"
pip3 install h5py

#!/bin/bash

set -e

echo "Using downloaded HDF5"
#python3 -m pip install requests
#python3 ci/get_hdf5.py
if [ -f $HDF5_DIR/lib/libhdf5.so ]; then
echo "using cached build"
else
    pushd /tmp
    #                             Remove trailing .*, to get e.g. '1.12' ↓
    wget "https://www.hdfgroup.org/ftp/HDF5/releases/hdf5-${HDF5_VERSION%.*}/hdf5-$HDF5_VERSION/src/hdf5-$HDF5_VERSION.tar.gz"
    tar -xzvf hdf5-$HDF5_VERSION.tar.gz
    pushd hdf5-$HDF5_VERSION
    chmod u+x autogen.sh
    if [[ "${HDF5_VERSION%.*}" = "1.12" ]]; then
        ./configure --prefix $HDF5_DIR
    else
        ./configure --prefix $HDF5_DIR
    fi
    make -j $(nproc)
    make install
    popd
    popd
fi

git clone https://github.com/readdy/readdy
pip3 install ./readdy

pip3 install .

pip3 install cibuildwheel==1.6.1