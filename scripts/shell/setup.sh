#!/bin/bash

# Download GPT-2-ja small pretrained model
wget https://www.nama.ne.jp/models/gpt2ja-small.tar.bz2

# Unzip
tar xvfj gpt2ja-small.tar.bz2

# Remove bz2 file
rm gpt2ja-small.tar.bz2
