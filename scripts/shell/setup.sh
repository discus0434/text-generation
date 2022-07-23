#!/bin/bash

# Download pretrained models
wget https://www.nama.ne.jp/models/gpt2ja-small.tar.bz2
wget https://www.nama.ne.jp/models/RoBERTa-ja_base.tar.bz2

# Unzip
tar xvfj gpt2ja-small.tar.bz2
tar xvfj RoBERTa-ja_base.tar.bz2

# Remove bz2 file
rm gpt2ja-small.tar.bz2
rm RoBERTa-ja_base.tar.bz2

