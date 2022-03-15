FROM ubuntu:20.04
ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
RUN apt-get update

RUN apt-get install -y wget git build-essential && rm -rf /var/lib/apt/lists/*

RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh
RUN conda --version
WORKDIR /home

# install python packages
COPY conda.env conda.env
RUN conda create --file conda.env --name hydrogels && \
    /bin/bash -c "source activate hydrogels" && \
    pip install softnanotools pybind11

# install cmake
RUN apt-get update \
    && apt-get install -y build-essential libssl-dev \
    && cd /tmp \
    && wget https://github.com/Kitware/CMake/releases/download/v3.20.0/cmake-3.20.0.tar.gz \
    && tar -zxvf cmake-3.20.0.tar.gz \
    && cd cmake-3.20.0 \
    && ./bootstrap \
    && make -j4 \
    && make install \
    && cmake --version \
    && cd .. \
    && rm -rf cmake* \
    && cd /home

# install oxDNA
ENV PATH="/home/oxDNA_bin:${PATH}"
ARG PATH="/home/oxDNA_bin:${PATH}"
RUN git clone https://github.com/lorenzo-rovigatti/oxDNA \
    && cd oxDNA \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make -j4 \
    && make rovigatti -j4 \
    && mv bin /home/oxDNA_bin \
    && cd /home \
    && rm -rf oxDNA

# install LAMMPS
ENV PATH="/home/lammps_bin:${PATH}"
ARG PATH="/home/lammps_bin:${PATH}"
RUN git clone https://github.com/lammps/lammps \
    && cd lammps \
    && mkdir build \
    && cd build \
    && cmake -DCMAKE_BUILD_TYPE=Release -DPKG_MOLECULE=yes -DPKG_CLASS2=yes -DPKG_KSPACE=yes -DPKG_PYTHON=yes ../cmake \
    && make -j4 \
    && mv lmp /usr/local/bin/lmp \
    && cd /home \
    && rm -rf lammps

# install hydrogels
COPY . hydrogels/
RUN pip install ./hydrogels

CMD ["/bin/bash", "-c", "source activate hydrogels", "&&", "hydrogels"]
