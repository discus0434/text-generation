FROM nvidia/cuda:11.2.0-cudnn8-runtime-ubuntu18.04

SHELL ["/bin/bash", "-c"]

# Install essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git wget unzip python-pip libgl1-mesa-dev tar nano sudo systemd psmisc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Setup conda
RUN curl https://repo.anaconda.com/miniconda/Miniconda3-py39_4.10.3-Linux-x86_64.sh -o Miniconda3-py39_4.10.3-Linux-x86_64.sh
RUN bash Miniconda3-py39_4.10.3-Linux-x86_64.sh -b
ENV PATH=/root/miniconda3/bin:/usr/local/nvidia/bin:/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
RUN conda init bash
RUN conda update -y conda

# Clone a main repo and set as workdir
RUN git clone https://github.com/discus0434/text-generation.git
WORKDIR /text-generation

# Setup conda environment
RUN conda create -n textgen python=3.9
RUN echo "source activate textgen" > ~/.bashrc
RUN conda run -n textgen pip install -r requirements.txt

RUN chmod +x scripts/shell/setup.sh
RUN chmod +x scripts/shell/finetune.sh
RUN chmod +x scripts/shell/generate.sh

RUN scripts/shell/setup.sh
