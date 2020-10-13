if [[ "$TRAVIS_OS_NAME" != "linux" ]]; then
    echo "LINUX"
    wget https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.12/hdf5-1.12.0/src/CMake-hdf5-1.12.0.tar.gz
    tar xzf CMake-hdf5-1.12.0.tar.gz 
    pushd CMake-hdf5-1.12.0
    ./build-unix.sh
    popd # leaving hdf5 directory
elif [[ "$TRAVIS_OS_NAME" == "osx" ]]; then
    echo "OSX"
    wget https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.12/hdf5-1.12.0/src/CMake-hdf5-1.12.0.tar.gz
    tar xzf CMake-hdf5-1.12.0.tar.gz 
    pushd CMake-hdf5-1.12.0
    ./build-unix.sh
    popd # leaving hdf5 directory
elif [[ "$TRAVIS_OS_NAME" == "windows" ]]; then
    choco install zip
    wget https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.12/hdf5-1.12.0/src/CMake-hdf5-1.12.0.zip
    tar.exe -x -f CMake-hdf5-1.12.0.zip
    pushd CMake-hdf5-1.12.0
    build-VS2017-64
    popd # leaving hdf5 directory
fi;

pip3 install --upgrade pip setuptools wheel
pip3 install numpy
pip3 install scipy
pip3 install pandas
pip3 install matplotlib

pip3 install "pybind11"
pip3 install h5py

git clone https://github.com/readdy/readdy
pip3 install ./readdy

# install hydrogels
pip3 install .

pip3 install cibuildwheel==1.6.1