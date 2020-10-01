python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install numpy
python3 -m pip install scipy
python3 -m pip install pandas
python3 -m pip install matplotlib

python3 -m pip install "pybind11[global]"
python3 -m pip install h5py

git clone https://github.com/readdy/readdy
python3 -m pip install ./readdy

python3 -m pip install .

python3 -m pip install cibuildwheel==1.6.1